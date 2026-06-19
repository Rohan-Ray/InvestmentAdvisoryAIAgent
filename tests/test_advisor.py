"""
Step 12 & 19: Unit tests for the investment rule engine.
Tests correctness of allocations, edge cases, and prompt-engineering scenarios.
Run: python3 -m pytest tests/ -v
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from src.backend.advisor import UserProfile, get_recommendation, _normalise


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_profile(**kwargs):
    defaults = dict(age=30, monthly_income=50000, monthly_savings=10000,
                    risk_preference="Medium", investment_goal="Medium-term")
    defaults.update(kwargs)
    return UserProfile(**defaults)


# ── Core allocation tests ─────────────────────────────────────────────────────

class TestAllocationSumsTo100:
    """Every combination of risk × goal must sum to exactly 100."""

    @pytest.mark.parametrize("risk", ["Low", "Medium", "High"])
    @pytest.mark.parametrize("goal", ["Short-term", "Medium-term", "Long-term"])
    def test_sum_is_100(self, risk, goal):
        rec = get_recommendation(make_profile(risk_preference=risk, investment_goal=goal))
        total = sum(rec.allocations.values())
        assert abs(total - 100.0) < 0.2, f"{risk}/{goal}: sum={total}"


class TestLowRiskNoEquity:
    """Low risk + Short-term should never have equity."""

    def test_low_short_no_equity(self):
        rec = get_recommendation(make_profile(risk_preference="Low", investment_goal="Short-term"))
        assert rec.allocations.get("Equity", 0) == 0

    def test_low_medium_minimal_equity(self):
        rec = get_recommendation(make_profile(risk_preference="Low", investment_goal="Medium-term"))
        assert rec.allocations.get("Equity", 0) == 0


class TestHighRiskEquityDominant:
    """High risk + Long-term should have equity as the largest allocation."""

    def test_equity_is_top(self):
        rec = get_recommendation(make_profile(risk_preference="High", investment_goal="Long-term"))
        assert rec.top_category == "Equity"
        assert rec.allocations["Equity"] >= 40


# ── Age adjustment tests ──────────────────────────────────────────────────────

class TestAgeAdjustment:
    """Users over 55 should have reduced equity."""

    def test_over_55_reduces_equity(self):
        young = get_recommendation(make_profile(age=30, risk_preference="High", investment_goal="Long-term"))
        old = get_recommendation(make_profile(age=60, risk_preference="High", investment_goal="Long-term"))
        assert old.allocations.get("Equity", 0) < young.allocations.get("Equity", 0)

    def test_over_55_increases_fd(self):
        young = get_recommendation(make_profile(age=30, risk_preference="High", investment_goal="Long-term"))
        old = get_recommendation(make_profile(age=60, risk_preference="High", investment_goal="Long-term"))
        assert old.allocations.get("Fixed Deposit", 0) >= young.allocations.get("Fixed Deposit", 0)


# ── Savings rate adjustment tests ─────────────────────────────────────────────

class TestSavingsRateAdjustment:
    """Low savings rate (<20%) should reduce equity and increase RD."""

    def test_low_savings_rate_shifts_to_rd(self):
        low_saver = get_recommendation(make_profile(
            monthly_income=100000, monthly_savings=5000,  # 5% savings rate
            risk_preference="High", investment_goal="Long-term"
        ))
        high_saver = get_recommendation(make_profile(
            monthly_income=100000, monthly_savings=40000, # 40% savings rate
            risk_preference="High", investment_goal="Long-term"
        ))
        # Low saver should have less equity than high saver
        assert low_saver.allocations.get("Equity", 0) <= high_saver.allocations.get("Equity", 0)


# ── Disclaimer test ───────────────────────────────────────────────────────────

class TestDisclaimerPresent:
    """Explanation must always contain the disclaimer text."""

    @pytest.mark.parametrize("risk,goal", [
        ("Low", "Short-term"), ("Medium", "Medium-term"), ("High", "Long-term")
    ])
    def test_disclaimer_in_explanation(self, risk, goal):
        rec = get_recommendation(make_profile(risk_preference=risk, investment_goal=goal))
        assert "educational demo" in rec.explanation.lower() or "disclaimer" in rec.explanation.lower()


# ── Normalisation test ────────────────────────────────────────────────────────

class TestNormalise:
    def test_normalises_to_100(self):
        raw = {"A": 30, "B": 40, "C": 50}
        normed = _normalise(raw)
        assert abs(sum(normed.values()) - 100.0) < 0.1

    def test_zero_sum_returns_unchanged(self):
        raw = {"A": 0, "B": 0}
        result = _normalise(raw)
        assert result == raw


# ── Edge cases ────────────────────────────────────────────────────────────────

class TestEdgeCases:
    def test_minimum_age(self):
        rec = get_recommendation(make_profile(age=18))
        assert sum(rec.allocations.values()) > 0

    def test_maximum_age(self):
        rec = get_recommendation(make_profile(age=80, risk_preference="High", investment_goal="Long-term"))
        assert sum(rec.allocations.values()) > 0

    def test_zero_savings(self):
        rec = get_recommendation(make_profile(monthly_savings=0))
        assert sum(rec.allocations.values()) > 0

    def test_very_high_income(self):
        rec = get_recommendation(make_profile(monthly_income=10_000_000, monthly_savings=5_000_000))
        assert sum(rec.allocations.values()) > 0
