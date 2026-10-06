import json
import os

from src import config
from src.generate_data import simulate_panel
from src.analysis import (
    baseline_diagnostics,
    naive_post_comparison,
    difference_in_differences,
)
from src.finance import financial_analysis
from src.validation import ground_truth_check
from src.visuals import (
    plot_margin_sensitivity,
    plot_normalized_segment_trends,
)


def main():

    # -------------------------------
    # 1. Generate Data
    # -------------------------------
    print("Simulating customer panel...")
    df_panel = simulate_panel()

    # -------------------------------
    # 2. Analysis
    # -------------------------------
    baseline_diagnostics(df_panel)
    naive_post_comparison(df_panel)

    model = difference_in_differences(df_panel)

    print("\n=== Difference-in-Differences Regression ===")
    print(model.summary())

    # -------------------------------
    # 3. Financial Evaluation
    # -------------------------------
    financial_analysis(df_panel, model)

    # -------------------------------
    # 4. Ground-Truth Validation
    # -------------------------------
    validation = ground_truth_check(df_panel, model.params["treated:post"])

    # -------------------------------
    # 5. Generate Visuals
    # -------------------------------
    os.makedirs("outputs/figures", exist_ok=True)

    df_panel.to_parquet("outputs/figures/df_panel.parquet", index=False)
    plot_normalized_segment_trends(df_panel)
    
    # Calculate incremental spend for margin sensitivity
    total_post_weeks = config.WEEKS_POST + config.PERSISTENCE_WEEKS
    treated_mask = (
        (df_panel["treated"] == 1)
        & (df_panel["period"] == "post")
    )

    treated_customers = df_panel.loc[treated_mask, "customer_id"].nunique()
    incremental_spend = (
        model.params["treated:post"]
        * treated_customers
        * total_post_weeks
    )

    cashback_mask = (
        (df_panel["treated"] == 1)
        & (df_panel["period"] == "post")
        & (df_panel["week"] < config.WEEKS_PRE + config.WEEKS_POST)
    )

    cashback_cost = (
        df_panel.loc[cashback_mask, "spend"].sum()
        * config.CASHBACK_RATE
    )

    plot_margin_sensitivity(incremental_spend, cashback_cost)

    # -------------------------------
    # 6. Export Results (read by dashboard)
    # -------------------------------
    promo_spend_weekly = (
        df_panel.loc[cashback_mask, "spend"].sum()
        / treated_customers
        / config.WEEKS_POST
    )
    true_incremental_spend = (
        validation["true_lift"] * treated_customers * total_post_weeks
    )

    results = {
        "did_lift": round(float(model.params["treated:post"]), 4),
        "did_ci_95": [round(float(x), 4) for x in model.conf_int().loc["treated:post"]],
        "treated_customers": int(treated_customers),
        "avg_treated_promo_spend_weekly": round(float(promo_spend_weekly), 4),
        "incremental_spend": round(float(incremental_spend), 2),
        "cashback_cost": round(float(cashback_cost), 2),
        "break_even_margin": round(float(cashback_cost / incremental_spend), 4),
        "ground_truth": {
            **{k: round(float(v), 4) for k, v in validation.items()},
            "break_even_margin_at_true_lift": round(
                float(cashback_cost / true_incremental_spend), 4
            ),
        },
    }

    with open("outputs/simulation_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("\nSaved figures to outputs/figures/ and results to outputs/simulation_results.json")


if __name__ == "__main__":
    main()