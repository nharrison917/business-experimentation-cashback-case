import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from . import config


def plot_treated_vs_control(df_panel, save_path="outputs/figures/spend_trends.png"):
    """
    Plot average weekly spend for treated vs control groups.
    """

    summary = (
        df_panel
        .groupby(["week", "treated"])["spend"]
        .mean()
        .reset_index()
    )

    pivot = summary.pivot(index="week", columns="treated", values="spend")

    plt.figure(figsize=(10, 6))

    plt.plot(pivot.index, pivot[0], label="Control", linewidth=2)
    plt.plot(pivot.index, pivot[1], label="Treated", linewidth=2)

    # Promo start line
    promo_start = config.WEEKS_PRE
    plt.axvline(x=promo_start, linestyle="--", alpha=0.6)

    plt.title("Average Weekly Spend: Treated vs Control")
    plt.xlabel("Week")
    plt.ylabel("Average Spend")
    plt.legend()
    plt.tight_layout()

    plt.savefig(save_path, dpi=300)
    plt.close()


def plot_margin_sensitivity(incremental_spend, cashback_cost,
                            save_path="outputs/figures/margin_sensitivity.png"):
    """
    Plot incremental profit vs revenue margin.
    """

    margins = np.linspace(0.01, 0.15, 100)

    profits = (incremental_spend * margins) - cashback_cost

    plt.figure(figsize=(10, 6))
    plt.plot(margins, profits, linewidth=2)

    plt.axhline(0, linestyle="--", alpha=0.6)

    plt.title("Incremental Profit vs Revenue Margin")
    plt.xlabel("Revenue Margin")
    plt.ylabel("Incremental Profit")
    plt.tight_layout()

    plt.savefig(save_path, dpi=300)
    plt.close()


def plot_three_segment_trends(df_panel, save_path="outputs/figures/three_segment_trends.png"):
    """
    Plot average weekly spend for:
    - Low (< threshold)
    - Mid (targeted segment)
    - High (>= upper bound)
    """

    # Create spend segment label based on pre-period average
    pre_avg = (
        df_panel[df_panel["period"] == "pre"]
        .groupby("customer_id")["spend"]
        .mean()
        .reset_index()
        .rename(columns={"spend": "avg_pre_spend"})
    )

    def segment(row):
        if row < 125:
            return "Low"
        elif row < 300:
            return "Mid (Targeted)"
        else:
            return "High"

    pre_avg["segment"] = pre_avg["avg_pre_spend"].apply(segment)

    df_panel = df_panel.merge(
        pre_avg[["customer_id", "segment"]],
        on="customer_id",
        how="left"
    )

    summary = (
        df_panel
        .groupby(["week", "segment"])["spend"]
        .mean()
        .reset_index()
    )

    pivot = summary.pivot(index="week", columns="segment", values="spend")

    plt.figure(figsize=(10, 6))

    for col in pivot.columns:
        plt.plot(pivot.index, pivot[col], label=col, linewidth=2)

    promo_start = config.WEEKS_PRE
    plt.axvline(x=promo_start, linestyle="--", alpha=0.6)

    plt.title("Average Weekly Spend by Segment")
    plt.xlabel("Week")
    plt.ylabel("Average Spend")
    plt.legend()
    plt.tight_layout()

    plt.savefig(save_path, dpi=300)
    plt.close()


def plot_normalized_segment_trends(df_panel, save_path="outputs/figures/normalized_segment_trends.png"):
    """
    Plot normalized weekly spend (indexed to 100 at Week 0)
    for Low, Mid (Targeted), and High segments.
    """

    pre_avg = (
        df_panel[df_panel["period"] == "pre"]
        .groupby("customer_id")["spend"]
        .mean()
        .reset_index()
        .rename(columns={"spend": "avg_pre_spend"})
    )

    def segment(row):
        if row < 125:
            return "Low"
        elif row < 300:
            return "Mid (Targeted)"
        else:
            return "High"

    pre_avg["segment"] = pre_avg["avg_pre_spend"].apply(segment)

    df_panel = df_panel.merge(
        pre_avg[["customer_id", "segment"]],
        on="customer_id",
        how="left"
    )

    summary = (
        df_panel
        .groupby(["week", "segment"])["spend"]
        .mean()
        .reset_index()
    )

    pivot = summary.pivot(index="week", columns="segment", values="spend")

    # Normalize to Week 0 = 100
    pivot_norm = pivot.div(pivot.iloc[0]).mul(100)

    plt.figure(figsize=(10, 6))

    for col in pivot_norm.columns:
        plt.plot(pivot_norm.index, pivot_norm[col], label=col, linewidth=2)

    promo_start = config.WEEKS_PRE
    plt.axvline(x=promo_start, linestyle="--", alpha=0.6)

    plt.title("Normalized Spend Index (Week 0 = 100)")
    plt.xlabel("Week")
    plt.ylabel("Spend Index")
    plt.legend()
    plt.tight_layout()

    plt.savefig(save_path, dpi=300)
    plt.close()