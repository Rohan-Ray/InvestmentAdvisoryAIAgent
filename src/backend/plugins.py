"""
Step 10: Internal tool plugins for sub-agents.
These are callable Python functions exposed as tools to backend-agent and frontend-agent.
"""

from typing import Any
from .advisor import UserProfile, get_recommendation, InvestmentRecommendation


# ── Tool: investment_rule_engine ──────────────────────────────────────────────

def investment_rule_engine(
    age: int,
    monthly_income: float,
    monthly_savings: float,
    risk_preference: str,
    investment_goal: str,
) -> dict[str, Any]:
    """
    Internal plugin tool: run the investment rule engine and return allocations.
    Used by backend-agent to validate rule correctness.
    """
    profile = UserProfile(
        age=age,
        monthly_income=monthly_income,
        monthly_savings=monthly_savings,
        risk_preference=risk_preference,
        investment_goal=investment_goal,
    )
    rec = get_recommendation(profile)
    return {
        "allocations": rec.allocations,
        "top_category": rec.top_category,
        "risk_label": rec.risk_label,
        "horizon_label": rec.horizon_label,
        "allocations_sum": sum(rec.allocations.values()),
    }


# ── Tool: portfolio_allocator ─────────────────────────────────────────────────

def portfolio_allocator(
    monthly_savings: float,
    allocations: dict[str, float],
) -> dict[str, float]:
    """
    Internal plugin tool: convert percentage allocations to rupee amounts.
    Used by frontend-agent to populate the breakdown table.
    """
    return {
        category: round(monthly_savings * pct / 100, 2)
        for category, pct in allocations.items()
    }


# ── Tool: risk_profiler ───────────────────────────────────────────────────────

def risk_profiler(
    age: int,
    monthly_income: float,
    monthly_savings: float,
    risk_preference: str,
) -> dict[str, Any]:
    """
    Internal plugin tool: derive a composite risk score from user attributes.
    Score: 0 (most conservative) → 10 (most aggressive).
    """
    # Base score from risk preference
    base = {"Low": 2, "Medium": 5, "High": 8}.get(risk_preference, 5)

    # Age modifier: reduce score for older users
    if age >= 55:
        age_mod = -2
    elif age >= 45:
        age_mod = -1
    elif age <= 30:
        age_mod = +1
    else:
        age_mod = 0

    # Savings-rate modifier
    savings_rate = monthly_savings / monthly_income if monthly_income > 0 else 0
    savings_mod = +1 if savings_rate >= 0.30 else (-1 if savings_rate < 0.10 else 0)

    score = max(0, min(10, base + age_mod + savings_mod))
    label = "Conservative" if score <= 3 else ("Moderate" if score <= 6 else "Aggressive")

    return {
        "raw_score": score,
        "label": label,
        "components": {
            "base": base,
            "age_modifier": age_mod,
            "savings_modifier": savings_mod,
        },
    }


# ── Tool registry (for MCP and agent use) ────────────────────────────────────

TOOL_REGISTRY: dict[str, callable] = {
    "investment_rule_engine": investment_rule_engine,
    "portfolio_allocator": portfolio_allocator,
    "risk_profiler": risk_profiler,
}
