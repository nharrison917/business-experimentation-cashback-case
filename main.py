import os

import pandas as pd

from src import config
from src.generate_data import (
    generate_baseline_spend,
    generate_pre_period,
    assign_treatment,
    assign_compliance,
    generate_post_and_persistence,
)
from src.analysis import (
    baseline_diagnostics,
    naive_post_comparison,
    difference_in_differences,
)
from src.finance import financial_analysis
from src.visuals import (
    plot_margin_sensitivity,
    plot_normalized_segment_trends,
)


def main():

    # -------------------------------
    # 1. Generate Data
    # -------------------------------
    df_baseline = generate_baseline_spend()
    df_pre = generate_pre_period(df_baseline)

    df_treatment = assign_treatment(df_pre)
    df_treatment = assign_compliance(df_treatment)

    df_pre = df_pre.merge(
        df_treatment[["customer_id", "treated", "compliant"]],
        on="customer_id",
        how="left",
    )

    df_post = generate_post_and_persistence(df_baseline, df_treatment)

    df_panel = pd.concat([df_pre, df_post], ignore_index=True)

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
    # 4. Generate Visuals
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


if __name__ == "__main__":
    main()