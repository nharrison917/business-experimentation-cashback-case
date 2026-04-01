# -*- coding: utf-8 -*-
"""
Illustrative financial model for the dashboard.

The DiD lift estimate is treated as a fixed simulation output. Sliders
recalculate only the financial layer on top of it.

Constants are derived from the README summary figures (~$1.69M incremental
spend, ~$200K cashback cost at baseline assumptions). They will be close to
but not exactly the simulation output due to rounding in the README.

Compliance scaling: if compliance changes, the average lift per treated
customer scales proportionally (non-compliers contribute zero lift, so
they dilute the average). This is an approximation; the true effect would
require re-running the regression.
"""

# --- Fixed simulation outputs ---
DID_LIFT = 8.85            # $/customer/week, from DiD regression
TREATED_CUSTOMERS = 7_956  # customers in targeted mid-tier segment
AVG_TREATED_SPEND_WEEKLY = 209.50  # $/week average observed spend during promo

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
