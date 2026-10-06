# -*- coding: utf-8 -*-
"""
Illustrative financial model for the dashboard.

The DiD lift estimate is treated as a fixed simulation output. Sliders
recalculate only the financial layer on top of it.

Fixed simulation outputs are read from outputs/simulation_results.json,
which main.py writes. At baseline assumptions this module reproduces the
simulation's incremental spend and cashback cost exactly.

Compliance scaling: if compliance changes, the average lift per treated
customer scales proportionally (non-compliers contribute zero lift, so
they dilute the average). This is an approximation; the true effect would
require re-running the regression.
"""

import json
import os

# --- Fixed simulation outputs (written by main.py) ---
RESULTS_PATH = os.path.join(
    os.path.dirname(__file__), "..", "outputs", "simulation_results.json"
)

with open(RESULTS_PATH, encoding="utf-8") as _f:
    RESULTS = json.load(_f)

DID_LIFT = RESULTS["did_lift"]                    # $/customer/week, from DiD regression
TREATED_CUSTOMERS = RESULTS["treated_customers"]  # customers in targeted mid-tier segment
AVG_TREATED_SPEND_WEEKLY = RESULTS["avg_treated_promo_spend_weekly"]  # $/week during promo
TRUE_LIFT = RESULTS["ground_truth"]["true_lift"]  # simulation ground truth, for reference

# --- Fixed experiment design ---
WEEKS_POST = 4  # promo window length; not a slider

# --- Baseline financial assumptions (match config.py) ---
BASELINE_MARGIN = 0.06
BASELINE_PERSISTENCE = 20
BASELINE_COMPLIANCE = 0.65
BASELINE_CASHBACK = 0.03


def recalculate(margin, persistence_weeks, compliance_rate, cashback_rate):
    """
    Recalculate KPIs under adjusted financial assumptions.

    Parameters
    ----------
    margin : float
        Issuer revenue margin as a decimal (e.g. 0.06 = 6%).
    persistence_weeks : int
        Weeks of behavioral persistence after promo ends.
    compliance_rate : float
        Fraction of treated customers who respond (e.g. 0.65 = 65%).
    cashback_rate : float
        Cashback applied to treated spend during promo (e.g. 0.03 = 3%).

    Returns
    -------
    dict with keys: treated_customers, did_lift, incremental_spend,
    cashback_cost, net_profit, break_even_margin.
    """
    adjusted_lift = DID_LIFT * (compliance_rate / BASELINE_COMPLIANCE)
    total_post_weeks = WEEKS_POST + persistence_weeks
    incremental_spend = adjusted_lift * TREATED_CUSTOMERS * total_post_weeks

    total_promo_spend = AVG_TREATED_SPEND_WEEKLY * TREATED_CUSTOMERS * WEEKS_POST
    cashback_cost = cashback_rate * total_promo_spend

    net_profit = (incremental_spend * margin) - cashback_cost
    break_even_margin = (
        cashback_cost / incremental_spend if incremental_spend > 0 else float("inf")
    )

    return {
        "treated_customers": TREATED_CUSTOMERS,
        "did_lift": DID_LIFT,
        "incremental_spend": incremental_spend,
        "cashback_cost": cashback_cost,
        "net_profit": net_profit,
        "break_even_margin": break_even_margin,
    }


def baseline():
    """Return KPIs at baseline assumptions for delta calculation."""
    return recalculate(
        BASELINE_MARGIN,
        BASELINE_PERSISTENCE,
        BASELINE_COMPLIANCE,
        BASELINE_CASHBACK,
    )
