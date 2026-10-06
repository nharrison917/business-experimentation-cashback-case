# -*- coding: utf-8 -*-
"""
Ground-truth validation of the DiD estimate.

Because the data is simulated, the true causal effect is knowable: re-run the
simulation with identical seeds but the promotion switched off, and the
difference in treated post-period spend is the effect the promotion caused.

For a 2x2 DiD this gives an exact decomposition:

    DiD estimate = true lift + placebo DiD

where the placebo DiD is the estimate on the no-promotion panel (pure bias).
The placebo is further split by also removing the regression-to-mean drift.
"""

from . import config
from .analysis import difference_in_differences
from .generate_data import simulate_panel


def _treated_post_spend(df_panel):
    mask = (df_panel["treated"] == 1) & (df_panel["period"] == "post")
    return df_panel.loc[mask, "spend"].sum(), df_panel.loc[mask, "customer_id"].nunique()


def ground_truth_check(df_panel, did_effect, verbose=True):
    """
    Compare the DiD estimate against the simulation's true causal lift.

    Returns a dict of per-customer-per-week figures.
    """

    total_post_weeks = config.WEEKS_POST + config.PERSISTENCE_WEEKS
    no_decay = [0.0] * config.PERSISTENCE_WEEKS

    if verbose:
        print("\n=== Ground-Truth Validation ===")
        print("Re-simulating with promotion switched off (same seeds)...")

    df_no_promo = simulate_panel(treatment_lift=0.0, persistence_decay=no_decay)

    observed_spend, treated_customers = _treated_post_spend(df_panel)
    counterfactual_spend, _ = _treated_post_spend(df_no_promo)
    true_lift = (
        (observed_spend - counterfactual_spend)
        / treated_customers
        / total_post_weeks
    )

    placebo_did = difference_in_differences(df_no_promo).params["treated:post"]

    if verbose:
        print("Re-simulating with promotion and drift switched off...")

    df_clean = simulate_panel(
        treatment_lift=0.0, persistence_decay=no_decay, rtm_drift=0.0
    )
    placebo_no_drift = difference_in_differences(df_clean).params["treated:post"]

    # Exact identity for 2x2 DiD; guards against the decomposition drifting
    assert abs(did_effect - (true_lift + placebo_did)) < 1e-6

    results = {
        "did_estimate": did_effect,
        "true_lift": true_lift,
        "total_bias": placebo_did,
        "bias_rtm_drift": placebo_did - placebo_no_drift,
        "bias_trend_and_selection": placebo_no_drift,
        "overstatement_pct": placebo_did / true_lift,
    }

    if verbose:
        print(f"DiD estimate:                     ${did_effect:.2f}/customer/week")
        print(f"True causal lift:                 ${true_lift:.2f}/customer/week")
        print(f"Bias (placebo DiD, no promotion): ${placebo_did:.2f}")
        print(f"  - regression-to-mean drift:     ${results['bias_rtm_drift']:.2f}")
        print(f"  - level trend + selection:      ${placebo_no_drift:.2f}")
        print(f"DiD overstates true lift by {results['overstatement_pct']:.0%}")

    return results
