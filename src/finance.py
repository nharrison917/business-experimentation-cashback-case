import numpy as np
from . import config

def financial_analysis(df_panel, model, verbose=True):
    """
    Incremental financial evaluation.

    - Revenue accrues over all post + persistence weeks
    - Cashback applies only during promo weeks
    - Counterfactual removes DiD incremental lift
    """

    did_effect = model.params["treated:post"]
    ci_lower = model.conf_int().loc["treated:post"][0]

    total_post_weeks = config.WEEKS_POST + config.PERSISTENCE_WEEKS

    # -------------------------------
    # Masks
    # -------------------------------
    treated_all_mask = (
        (df_panel["treated"] == 1)
        & (df_panel["period"] == "post")
    )

    promo_mask = (
        treated_all_mask
        & (df_panel["week"] < config.WEEKS_PRE + config.WEEKS_POST)
    )

    # -------------------------------
    # Observed Spend
    # -------------------------------
    observed_total_spend = df_panel.loc[treated_all_mask, "spend"].sum()
    treated_customers = df_panel.loc[treated_all_mask, "customer_id"].nunique()

    observed_cashback = (
        df_panel.loc[promo_mask, "spend"].sum()
        * config.CASHBACK_RATE
    )

    # -------------------------------
    # Counterfactual Spend
    # -------------------------------
    counterfactual_total_spend = (
        observed_total_spend
        - (did_effect * treated_customers * total_post_weeks)
    )

    # -------------------------------
    # Revenue
    # -------------------------------
    observed_revenue = (
        observed_total_spend * config.ISSUER_REVENUE_RATE
    )

    counterfactual_revenue = (
        counterfactual_total_spend * config.ISSUER_REVENUE_RATE
    )

    incremental_profit = (
        (observed_revenue - observed_cashback)
        - counterfactual_revenue
    )

    roi = (
        incremental_profit / observed_cashback
        if observed_cashback != 0 else np.nan
    )

    # -------------------------------
    # Lower Bound Scenario
    # -------------------------------
    counterfactual_total_spend_lower = (
        observed_total_spend
        - (ci_lower * treated_customers * total_post_weeks)
    )

    counterfactual_revenue_lower = (
        counterfactual_total_spend_lower
        * config.ISSUER_REVENUE_RATE
    )

    incremental_profit_lower = (
        (observed_revenue - observed_cashback)
        - counterfactual_revenue_lower
    )

    roi_lower = (
        incremental_profit_lower / observed_cashback
        if observed_cashback != 0 else np.nan
    )

    if verbose:
        print("\n=== Financial Impact ===")
        print(f"Observed treated spend (all post weeks): ${observed_total_spend:,.2f}")
        print(f"Counterfactual treated spend: ${counterfactual_total_spend:,.2f}")
        print(f"Incremental lift per week: ${did_effect:.2f}")
        print(f"Observed cashback cost (promo weeks only): ${observed_cashback:,.2f}")
        print(f"Incremental profit: ${incremental_profit:,.2f}")
        print(f"ROI: {roi:.2%}")

        print("\n--- Lower Bound Scenario ---")
        print(f"ROI (lower bound): {roi_lower:.2%}")

    return {
        "incremental_profit": incremental_profit,
        "roi": roi,
        "roi_lower": roi_lower
    }