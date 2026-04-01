import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import plotly.graph_objects as go
from . import config



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
    plt.ylabel("Incremental Profit ($)")
    plt.gca().xaxis.set_major_formatter(mticker.PercentFormatter(xmax=1.0))
    plt.tight_layout()

    plt.savefig(save_path, dpi=300)
    plt.close()


def plotly_margin_sensitivity(incremental_spend, cashback_cost, highlight_margin=None):
    """
    Return a Plotly Figure: incremental profit vs revenue margin.
    highlight_margin marks the current slider value with a vertical line.
    """
    margins = np.linspace(0.01, 0.20, 200)
    profits = (incremental_spend * margins) - cashback_cost

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=margins * 100,
        y=profits,
        mode="lines",
        line=dict(width=2),
        name="Incremental Profit",
    ))

    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.6)

    if highlight_margin is not None:
        fig.add_vline(
            x=highlight_margin * 100,
            line_dash="dot",
            line_color="steelblue",
            opacity=0.8,
            annotation_text=f"{highlight_margin:.0%}",
            annotation_position="top right",
        )

    fig.update_layout(
        title="Incremental Profit vs Revenue Margin",
        xaxis_title="Revenue Margin (%)",
        yaxis_title="Incremental Profit ($)",
        yaxis_tickformat="$,.0f",
        hovermode="x unified",
        template="plotly_white",
    )

    return fig


def plotly_normalized_segment_trends(df_panel, max_week=None):
    """
    Return a Plotly Figure: normalized weekly spend indexed to Week 0 = 100,
    by Low / Mid (Targeted) / High segment.

    max_week: if set, truncates display at that week (used by persistence slider).
    """
    pre_avg = (
        df_panel[df_panel["period"] == "pre"]
        .groupby("customer_id")["spend"]
        .mean()
        .reset_index()
        .rename(columns={"spend": "avg_pre_spend"})
    )

    def segment(val):
        if val < 125:
            return "Low"
        elif val < 300:
            return "Mid (Targeted)"
        else:
            return "High"

    pre_avg["segment"] = pre_avg["avg_pre_spend"].apply(segment)

    df = df_panel.merge(
        pre_avg[["customer_id", "segment"]],
        on="customer_id",
        how="left",
    )

    summary = (
        df.groupby(["week", "segment"])["spend"]
        .mean()
        .reset_index()
    )

    pivot = summary.pivot(index="week", columns="segment", values="spend")

    if max_week is not None:
        pivot = pivot[pivot.index <= max_week]

    pivot_norm = pivot.div(pivot.iloc[0]).mul(100)

    fig = go.Figure()

    for col in pivot_norm.columns:
        fig.add_trace(go.Scatter(
            x=pivot_norm.index,
            y=pivot_norm[col],
            mode="lines",
            line=dict(width=2),
            name=col,
        ))

    fig.add_vline(
        x=config.WEEKS_PRE,
        line_dash="dash",
        line_color="gray",
        opacity=0.6,
        annotation_text="Promo Start",
        annotation_position="top right",
    )

    fig.update_layout(
        title="Normalized Spend Index (Week 0 = 100)",
        xaxis_title="Week",
        yaxis_title="Spend Index",
        hovermode="x unified",
        template="plotly_white",
    )

    return fig


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
    plt.axvline(x=promo_start, linestyle="--", alpha=0.6, label="Promo Start")

    plt.title("Normalized Spend Index (Week 0 = 100)")
    plt.xlabel("Week")
    plt.ylabel("Spend Index")
    plt.legend()
    plt.tight_layout()

    plt.savefig(save_path, dpi=300)
    plt.close()