# ================================
# generate_data.py
# Cashback Experiment – Data Generation
# Phase 1: Baseline Distribution
# ================================

import numpy as np
import pandas as pd

from . import config


def generate_baseline_spend():
    """
    Generate baseline weekly spend for N customers
    using a log-normal distribution.
    """

    np.random.seed(config.RANDOM_SEED)

    # Draw log-normal weekly spend
    baseline_weekly_spend = np.random.lognormal(
        mean=config.LOGNORMAL_MEAN,
        sigma=config.LOGNORMAL_SIGMA,
        size=config.N_CUSTOMERS
    )

    df = pd.DataFrame({
        "customer_id": np.arange(config.N_CUSTOMERS),
        "baseline_weekly_spend": baseline_weekly_spend
    })

    return df


def print_diagnostics(df):
    """
    Print summary statistics to validate distribution.
    """

    print("\n=== Baseline Weekly Spend Diagnostics ===\n")

    print(f"Mean weekly spend: ${df['baseline_weekly_spend'].mean():.2f}")
    print(f"Median weekly spend: ${df['baseline_weekly_spend'].median():.2f}")
    print(f"Min weekly spend: ${df['baseline_weekly_spend'].min():.2f}")
    print(f"Max weekly spend: ${df['baseline_weekly_spend'].max():.2f}")

    pct_below_threshold = (
        (df["baseline_weekly_spend"] < config.WEEKLY_THRESHOLD).mean() * 100
    )

    print(f"\n% Below Weekly Target Threshold (${config.WEEKLY_THRESHOLD:.2f}): "
          f"{pct_below_threshold:.2f}%")

    print("\n=========================================\n")


def generate_pre_period(df_baseline):
    """
    Expand baseline spend into 8-week pre-period panel.
    Adds volatility and macro trend.
    """

    records = []

    for week in range(config.WEEKS_PRE):

        # Macro trend multiplier
        macro_multiplier = 1 + (week * config.MACRO_TREND_WEEKLY)

        # Random noise per customer
        noise = np.random.normal(
            loc=0,
            scale=config.WEEKLY_VOLATILITY,
            size=len(df_baseline)
        )

        weekly_spend = (
            df_baseline["baseline_weekly_spend"].values
            * macro_multiplier
            * (1 + noise)
        )

        week_df = pd.DataFrame({
            "customer_id": df_baseline["customer_id"],
            "week": week,
            "period": "pre",
            "spend": weekly_spend
        })

        records.append(week_df)

    df_pre = pd.concat(records, ignore_index=True)

    return df_pre

def assign_treatment(df_pre):
    """
    Assign treatment to mid-tier spenders:
    $125 <= weekly spend < $300
    """

    pre_avg = (
        df_pre.groupby("customer_id")["spend"]
        .mean()
        .reset_index()
        .rename(columns={"spend": "avg_pre_spend"})
    )

    pre_avg["treated"] = (
        (pre_avg["avg_pre_spend"] >= 125)
        & (pre_avg["avg_pre_spend"] < 300)
    ).astype(int)

    return pre_avg

def assign_compliance(df_treatment):
    """
    Assign compliance among treated customers.
    """

    np.random.seed(config.RANDOM_SEED + 1)

    df_treatment["compliant"] = 0

    treated_mask = df_treatment["treated"] == 1

    df_treatment.loc[treated_mask, "compliant"] = (
        np.random.rand(treated_mask.sum()) < config.COMPLIANCE_RATE
    ).astype(int)

    return df_treatment

def generate_post_and_persistence(df_baseline, df_treatment):
    """
    Generate promo + persistence weeks.
    Applies:
    - 12% lift during promo (4 weeks)
    - Decaying persistence afterward
    """

    records = []

    total_post_weeks = config.WEEKS_POST + config.PERSISTENCE_WEEKS

    for i in range(total_post_weeks):

        global_week = config.WEEKS_PRE + i
        macro_multiplier = 1 + (global_week * config.MACRO_TREND_WEEKLY)

        noise = np.random.normal(
            loc=0,
            scale=config.WEEKLY_VOLATILITY,
            size=len(df_baseline)
        )

        base_spend = (
            df_baseline["baseline_weekly_spend"].values
            * macro_multiplier
            * (1 + noise)
        )

        df_week = pd.DataFrame({
            "customer_id": df_baseline["customer_id"],
            "week": global_week,
            "period": "post",
            "spend": base_spend
        })

        df_week["spend"] = df_week["spend"].clip(lower=0)

        df_week = df_week.merge(
            df_treatment[["customer_id", "treated", "compliant"]],
            on="customer_id",
            how="left"
        )

        # Regression-to-mean drift
        df_week.loc[df_week["treated"] == 1, "spend"] *= (
            1 + config.REGRESSION_TO_MEAN
        )

        # Determine lift
        if i < config.WEEKS_POST:
            lift = config.TREATMENT_LIFT
        else:
            decay_index = i - config.WEEKS_POST
            lift = config.PERSISTENCE_DECAY[decay_index]

        treatment_mask = (
            (df_week["treated"] == 1)
            & (df_week["compliant"] == 1)
        )

        df_week.loc[treatment_mask, "spend"] *= (1 + lift)

        records.append(df_week)

    return pd.concat(records, ignore_index=True)

