"""
Investment Advisory Rule Engine
Rule-based logic for educational investment recommendations.
No real financial advice is provided.
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class UserProfile:
    age: int
    monthly_income: float
    monthly_savings: float
    risk_preference: str   # "Low", "Medium", "High"
    investment_goal: str   # "Short-term", "Medium-term", "Long-term"


@dataclass
class InvestmentRecommendation:
    allocations: Dict[str, float]        # category -> percentage
    explanation: str
    risk_label: str
    horizon_label: str
    top_category: str


# Base allocation templates indexed by (risk, goal)
_BASE_ALLOCATIONS = {
    ("Low", "Short-term"):   {"Fixed Deposit": 50, "Recurring Deposit": 30, "Bonds": 15, "Mutual Funds": 5,  "Equity": 0},
    ("Low", "Medium-term"):  {"Fixed Deposit": 35, "Recurring Deposit": 25, "Bonds": 25, "Mutual Funds": 15, "Equity": 0},
    ("Low", "Long-term"):    {"Fixed Deposit": 25, "Recurring Deposit": 20, "Bonds": 30, "Mutual Funds": 20, "Equity": 5},
    ("Medium", "Short-term"):{"Fixed Deposit": 30, "Recurring Deposit": 25, "Bonds": 20, "Mutual Funds": 20, "Equity": 5},
    ("Medium", "Medium-term"):{"Fixed Deposit": 20, "Recurring Deposit": 15, "Bonds": 20, "Mutual Funds": 30, "Equity": 15},
    ("Medium", "Long-term"): {"Fixed Deposit": 15, "Recurring Deposit": 10, "Bonds": 15, "Mutual Funds": 35, "Equity": 25},
    ("High", "Short-term"):  {"Fixed Deposit": 15, "Recurring Deposit": 10, "Bonds": 15, "Mutual Funds": 30, "Equity": 30},
    ("High", "Medium-term"): {"Fixed Deposit": 10, "Recurring Deposit": 5,  "Bonds": 10, "Mutual Funds": 35, "Equity": 40},
    ("High", "Long-term"):   {"Fixed Deposit": 5,  "Recurring Deposit": 5,  "Bonds": 10, "Mutual Funds": 30, "Equity": 50},
}

# Age-based adjustment: over 55 shift 10% from Equity to Fixed Deposit
_AGE_CONSERVATIVE_THRESHOLD = 55
_AGE_SHIFT = 10  # percentage points

# Savings-rate adjustment: savings < 20% of income → reduce equity exposure
_LOW_SAVINGS_RATE = 0.20


def _adjust_for_age(alloc: Dict[str, float], age: int) -> Dict[str, float]:
    """Reduce equity for older investors and reallocate to Fixed Deposit."""
    alloc = dict(alloc)
    if age >= _AGE_CONSERVATIVE_THRESHOLD and alloc.get("Equity", 0) >= _AGE_SHIFT:
        alloc["Equity"] -= _AGE_SHIFT
        alloc["Fixed Deposit"] = alloc.get("Fixed Deposit", 0) + _AGE_SHIFT
    return alloc


def _adjust_for_savings_rate(alloc: Dict[str, float], monthly_income: float, monthly_savings: float) -> Dict[str, float]:
    """Lower equity if savings rate is below 20% (less buffer for risk)."""
    alloc = dict(alloc)
    if monthly_income > 0:
        rate = monthly_savings / monthly_income
        if rate < _LOW_SAVINGS_RATE and alloc.get("Equity", 0) >= 5:
            shift = 5
            alloc["Equity"] -= shift
            alloc["Recurring Deposit"] = alloc.get("Recurring Deposit", 0) + shift
    return alloc


def _normalise(alloc: Dict[str, float]) -> Dict[str, float]:
    """Ensure allocations sum to exactly 100."""
    total = sum(alloc.values())
    if total == 0:
        return alloc
    return {k: round(v / total * 100, 1) for k, v in alloc.items()}


def _build_explanation(profile: UserProfile, alloc: Dict[str, float], top: str) -> str:
    """Generate a plain-language explanation of the recommendation."""
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


def get_recommendation(profile: UserProfile) -> InvestmentRecommendation:
    """
    Main entry point: returns an InvestmentRecommendation for the given UserProfile.
    Uses rule-based logic — no ML or real financial advice.
    """
    key = (profile.risk_preference, profile.investment_goal)
    alloc = dict(_BASE_ALLOCATIONS.get(key, _BASE_ALLOCATIONS[("Medium", "Medium-term")]))

    alloc = _adjust_for_age(alloc, profile.age)
    alloc = _adjust_for_savings_rate(alloc, profile.monthly_income, profile.monthly_savings)
    alloc = _normalise(alloc)

    # Remove zero-allocation categories for cleaner display
    alloc = {k: v for k, v in alloc.items() if v > 0}

    top = max(alloc, key=alloc.__getitem__)
    explanation = _build_explanation(profile, alloc, top)

    return InvestmentRecommendation(
        allocations=alloc,
        explanation=explanation,
        risk_label=profile.risk_preference,
        horizon_label=profile.investment_goal,
        top_category=top,
    )
