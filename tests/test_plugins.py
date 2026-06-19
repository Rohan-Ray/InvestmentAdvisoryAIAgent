"""Tests for internal plugin tools."""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from src.backend.plugins import investment_rule_engine, portfolio_allocator, risk_profiler


def test_rule_engine_sum():
    result = investment_rule_engine(30, 50000, 10000, "Medium", "Medium-term")
    assert abs(result["allocations_sum"] - 100.0) < 0.2


def test_portfolio_allocator_basic():
    allocs = {"Fixed Deposit": 50.0, "Equity": 50.0}
    result = portfolio_allocator(10000, allocs)
    assert result["Fixed Deposit"] == 5000.0
    assert result["Equity"] == 5000.0


def test_risk_profiler_low():
    result = risk_profiler(65, 30000, 2000, "Low")
    assert result["label"] == "Conservative"
    assert result["raw_score"] <= 3


def test_risk_profiler_high():
    result = risk_profiler(25, 100000, 40000, "High")
    assert result["label"] == "Aggressive"
    assert result["raw_score"] >= 7
