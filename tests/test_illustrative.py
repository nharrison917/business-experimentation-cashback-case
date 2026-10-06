# -*- coding: utf-8 -*-
"""Tests for the dashboard's illustrative financial layer."""

import json
import os

import pytest

from src import illustrative

RESULTS_PATH = os.path.join(
    os.path.dirname(__file__), "..", "outputs", "simulation_results.json"
)


@pytest.fixture
def results():
    with open(RESULTS_PATH, encoding="utf-8") as f:
        return json.load(f)


def test_baseline_reproduces_simulation(results):
    """At baseline assumptions, the illustrative layer matches main.py output."""
    base = illustrative.baseline()
    assert base["incremental_spend"] == pytest.approx(results["incremental_spend"], rel=1e-4)
    assert base["cashback_cost"] == pytest.approx(results["cashback_cost"], rel=1e-4)
    assert base["break_even_margin"] == pytest.approx(results["break_even_margin"], abs=1e-3)


def test_net_profit_zero_at_break_even():
    kpis = illustrative.baseline()
    at_be = illustrative.recalculate(
        kpis["break_even_margin"],
        illustrative.BASELINE_PERSISTENCE,
        illustrative.BASELINE_COMPLIANCE,
        illustrative.BASELINE_CASHBACK,
    )
    assert at_be["net_profit"] == pytest.approx(0, abs=1e-6)


def test_cashback_cost_scales_linearly():
    one = illustrative.recalculate(0.06, 20, 0.65, 0.01)
    three = illustrative.recalculate(0.06, 20, 0.65, 0.03)
    assert three["cashback_cost"] == pytest.approx(3 * one["cashback_cost"])
    assert three["incremental_spend"] == one["incremental_spend"]


def test_compliance_scales_lift_proportionally():
    base = illustrative.recalculate(0.06, 20, 0.65, 0.03)
    full = illustrative.recalculate(0.06, 20, 1.00, 0.03)
    assert full["incremental_spend"] == pytest.approx(base["incremental_spend"] / 0.65)


def test_zero_compliance_gives_infinite_break_even():
    kpis = illustrative.recalculate(0.06, 20, 0.0, 0.03)
    assert kpis["incremental_spend"] == 0
    assert kpis["break_even_margin"] == float("inf")


def test_ground_truth_decomposition_is_exact(results):
    gt = results["ground_truth"]
    assert gt["did_estimate"] == pytest.approx(gt["true_lift"] + gt["total_bias"], abs=1e-3)
    assert gt["total_bias"] == pytest.approx(
        gt["bias_rtm_drift"] + gt["bias_trend_and_selection"], abs=1e-3
    )
