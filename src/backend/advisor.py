"""
Investment Advisory — Hybrid Engine
Rule engine produces deterministic allocations.
Claude Sonnet 4.6 generates the full personalised investment plan narrative.
No real financial advice is provided.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import os
import time
import logging

from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

log = logging.getLogger(__name__)

def _get_metrics():
    """Lazy import of Prometheus metrics to avoid circular imports at module load time."""
    try:
        from observability.metrics_exporter import (
            recommendation_counter, recommendation_latency,
            claude_input_tokens, claude_output_tokens, claude_cost_usd,
        )
        return recommendation_counter, recommendation_latency, claude_input_tokens, claude_output_tokens, claude_cost_usd
    except Exception:
        return None, None, None, None, None

# ── Claude model & pricing ─────────────────────────────────────────────────────
_CLAUDE_MODEL              = "bedrock.anthropic.claude-sonnet-4-6"
_INPUT_PRICE_PER_M         = 3.00   # USD per 1M input tokens
_OUTPUT_PRICE_PER_M        = 15.00  # USD per 1M output tokens

# Running totals — updated on every API call, read by the metrics exporter
token_usage_totals: Dict[str, float] = {
    "input_tokens": 0.0,
    "output_tokens": 0.0,
    "cost_usd": 0.0,
}

# ── Data models ────────────────────────────────────────────────────────────────

@dataclass
class UserProfile:
    age: int
    monthly_income: float
    monthly_savings: float
    risk_preference: str   # "Low", "Medium", "High"
    investment_goal: str   # "Short-term", "Medium-term", "Long-term"


@dataclass
class InvestmentRecommendation:
    allocations: Dict[str, float]   # category -> percentage
    explanation: str                # Sonnet narrative (or static fallback)
    risk_label: str
    horizon_label: str
    top_category: str
    ai_powered: bool = field(default=False)  # True when Sonnet generated the plan

# ── Rule engine — allocations only ────────────────────────────────────────────

_BASE_ALLOCATIONS = {
    ("Low",    "Short-term"):  {"Fixed Deposit": 50, "Recurring Deposit": 30, "Bonds": 15, "Mutual Funds": 5,  "Equity": 0},
    ("Low",    "Medium-term"): {"Fixed Deposit": 35, "Recurring Deposit": 25, "Bonds": 25, "Mutual Funds": 15, "Equity": 0},
    ("Low",    "Long-term"):   {"Fixed Deposit": 25, "Recurring Deposit": 20, "Bonds": 30, "Mutual Funds": 20, "Equity": 5},
    ("Medium", "Short-term"):  {"Fixed Deposit": 30, "Recurring Deposit": 25, "Bonds": 20, "Mutual Funds": 20, "Equity": 5},
    ("Medium", "Medium-term"): {"Fixed Deposit": 20, "Recurring Deposit": 15, "Bonds": 20, "Mutual Funds": 30, "Equity": 15},
    ("Medium", "Long-term"):   {"Fixed Deposit": 15, "Recurring Deposit": 10, "Bonds": 15, "Mutual Funds": 35, "Equity": 25},
    ("High",   "Short-term"):  {"Fixed Deposit": 15, "Recurring Deposit": 10, "Bonds": 15, "Mutual Funds": 30, "Equity": 30},
    ("High",   "Medium-term"): {"Fixed Deposit": 10, "Recurring Deposit": 5,  "Bonds": 10, "Mutual Funds": 35, "Equity": 40},
    ("High",   "Long-term"):   {"Fixed Deposit": 5,  "Recurring Deposit": 5,  "Bonds": 10, "Mutual Funds": 30, "Equity": 50},
}

_AGE_CONSERVATIVE_THRESHOLD = 55
_LOW_SAVINGS_RATE = 0.20


def _compute_allocations(profile: UserProfile) -> Dict[str, float]:
    key   = (profile.risk_preference, profile.investment_goal)
    alloc = dict(_BASE_ALLOCATIONS.get(key, _BASE_ALLOCATIONS[("Medium", "Medium-term")]))

    # Age adjustment: over 55 → shift 10% from Equity to Fixed Deposit
    if profile.age >= _AGE_CONSERVATIVE_THRESHOLD and alloc.get("Equity", 0) >= 10:
        alloc["Equity"]        -= 10
        alloc["Fixed Deposit"]  = alloc.get("Fixed Deposit", 0) + 10

    # Low savings rate → reduce equity, boost Recurring Deposit
    if profile.monthly_income > 0:
        rate = profile.monthly_savings / profile.monthly_income
        if rate < _LOW_SAVINGS_RATE and alloc.get("Equity", 0) >= 5:
            alloc["Equity"]            -= 5
            alloc["Recurring Deposit"]  = alloc.get("Recurring Deposit", 0) + 5

    # Normalise to 100 %
    total = sum(alloc.values())
    if total:
        alloc = {k: round(v / total * 100, 1) for k, v in alloc.items()}

    return {k: v for k, v in alloc.items() if v > 0}


# ── Static fallback narrative (no API key) ────────────────────────────────────

def _static_explanation(profile: UserProfile, alloc: Dict[str, float], top: str) -> str:
    savings_rate = (profile.monthly_savings / profile.monthly_income * 100) if profile.monthly_income else 0
    lines: List[str] = [
        f"Based on your profile — Age {profile.age}, {profile.risk_preference} risk appetite, "
        f"and a {profile.investment_goal.lower()} goal — here is your suggested allocation:",
        "",
        "**Why this mix?**",
    ]
    if profile.risk_preference == "Low":
        lines.append("- You prefer safety. Fixed Deposits and Bonds protect your capital with predictable returns.")
    elif profile.risk_preference == "Medium":
        lines.append("- You balance safety and growth. A healthy Mutual Fund slice can beat inflation over time.")
    else:
        lines.append("- You are comfortable with market swings. Equity gives the highest long-term growth potential.")

    if profile.investment_goal == "Short-term":
        lines.append("- Short-term goals (< 3 years) need liquid, low-risk instruments.")
    elif profile.investment_goal == "Medium-term":
        lines.append("- Medium-term goals (3–7 years) benefit from a balanced mix.")
    else:
        lines.append("- Long-term goals (7+ years) allow time to ride out market volatility.")

    if profile.age >= _AGE_CONSERVATIVE_THRESHOLD:
        lines.append(f"- At age {profile.age}, your equity exposure has been reduced for capital preservation.")
    if savings_rate < _LOW_SAVINGS_RATE * 100:
        lines.append(f"- Your savings rate is {savings_rate:.1f}%. Building a Recurring Deposit habit helps create an emergency buffer.")

    lines += [
        "",
        f"**Top recommended instrument:** {top} ({alloc[top]:.1f}% of investable savings)",
        "",
        "> ⚠️ **DISCLAIMER:** This is an educational demo only. It does not constitute real financial advice. "
        "Please consult a SEBI-registered financial advisor before making any investment decisions.",
    ]
    return "\n".join(lines)


# ── Sonnet narrative generator ────────────────────────────────────────────────

_SYSTEM_PROMPT = """\
You are a helpful investment education assistant for a banking app.
Your job is to explain a pre-computed portfolio allocation in plain, friendly language.
The allocations are fixed by the bank's rule engine — you do NOT change them.
Write in second person ("you"). Use markdown with headers and bullet points.
Always end with a disclaimer that this is educational only and not real financial advice.
Do not invent numbers. Do not recommend specific funds or stocks by name.
"""

def _sonnet_explanation(profile: UserProfile, alloc: Dict[str, float], top: str) -> Optional[str]:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None

    savings_rate = (profile.monthly_savings / profile.monthly_income * 100) if profile.monthly_income else 0
    monthly_amounts = {k: round(profile.monthly_savings * v / 100, 0) for k, v in alloc.items()}

    user_prompt = f"""\
Customer profile:
- Age: {profile.age}
- Monthly income: ₹{profile.monthly_income:,.0f}
- Monthly savings available to invest: ₹{profile.monthly_savings:,.0f}
- Savings rate: {savings_rate:.1f}% of income
- Risk appetite: {profile.risk_preference}
- Investment goal horizon: {profile.investment_goal}

Portfolio allocation determined by the rule engine:
{chr(10).join(f"  - {k}: {v:.1f}%  (≈ ₹{monthly_amounts[k]:,.0f}/month)" for k, v in alloc.items())}

Top instrument: {top} at {alloc[top]:.1f}%

Write a personalised investment plan explanation for this customer covering:
1. Why this allocation suits their specific profile
2. What each instrument does for them (in simple terms)
3. Any profile-specific notes (age, savings rate, goal horizon)
4. A concrete next step they can take
"""

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model=_CLAUDE_MODEL,
            max_tokens=600,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
        usage = response.usage
        inp  = usage.input_tokens
        out  = usage.output_tokens
        cost = (inp / 1_000_000 * _INPUT_PRICE_PER_M
                + out / 1_000_000 * _OUTPUT_PRICE_PER_M)
        token_usage_totals["input_tokens"]  += inp
        token_usage_totals["output_tokens"] += out
        token_usage_totals["cost_usd"]      += cost
        _, _, ci, co, cc = _get_metrics()
        if ci is not None:
            ci.labels(model=_CLAUDE_MODEL).set(token_usage_totals["input_tokens"])
            co.labels(model=_CLAUDE_MODEL).set(token_usage_totals["output_tokens"])
            cc.labels(model=_CLAUDE_MODEL).set(token_usage_totals["cost_usd"])
        return next((b.text for b in response.content if b.type == "text"), None)
    except Exception as exc:
        log.warning("Sonnet explanation call failed: %s", exc)
        return None


# ── Public API ─────────────────────────────────────────────────────────────────

def get_recommendation(profile: UserProfile) -> InvestmentRecommendation:
    """
    Returns an InvestmentRecommendation.
    Allocations are rule-based (deterministic).
    Explanation is Sonnet-generated when ANTHROPIC_API_KEY is set, else static fallback.
    Records real Prometheus metrics on every call.
    """
    t0    = time.monotonic()
    alloc = _compute_allocations(profile)
    top   = max(alloc, key=alloc.__getitem__)

    sonnet_text = _sonnet_explanation(profile, alloc, top)
    if sonnet_text:
        explanation = sonnet_text
        ai_powered  = True
    else:
        explanation = _static_explanation(profile, alloc, top)
        ai_powered  = False

    latency_ms = (time.monotonic() - t0) * 1000

    rc, rl, _, _, _ = _get_metrics()
    if rc is not None:
        rc.labels(risk=profile.risk_preference, goal=profile.investment_goal).inc()
        rl.labels(risk=profile.risk_preference).observe(latency_ms)

    return InvestmentRecommendation(
        allocations=alloc,
        explanation=explanation,
        risk_label=profile.risk_preference,
        horizon_label=profile.investment_goal,
        top_category=top,
        ai_powered=ai_powered,
    )
