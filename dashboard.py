# -*- coding: utf-8 -*-
"""
Cashback Experiment -- Interactive Dashboard

Run:  streamlit run dashboard.py
Requires: main.py must be run first to generate outputs/figures/
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import pandas as pd

from src.illustrative import recalculate, baseline, TREATED_CUSTOMERS, DID_LIFT
from src.visuals import plotly_margin_sensitivity, plotly_normalized_segment_trends
from src import config

# -----------------------------------------------------------------------
# Page config
# -----------------------------------------------------------------------
st.set_page_config(
    page_title="Cashback Promotion: Economic Viability",
    layout="wide",
)

# -----------------------------------------------------------------------
# Sidebar -- assumption sliders
# -----------------------------------------------------------------------
with st.sidebar:
    st.header("Adjust Assumptions")
    st.caption("Behavioral lift held fixed at DiD result. Sliders adjust financial assumptions only.")
    st.divider()

    margin_pct = st.slider(
        "Revenue Margin",
        min_value=1, max_value=20, value=6, step=1,
        format="%d%%",
        help="Blended issuer revenue rate (interchange + network economics).",
    )
    margin = margin_pct / 100

    persistence_weeks = st.slider(
        "Behavioral Persistence (weeks)",
        min_value=8, max_value=32, value=20, step=1,
        help="Weeks of decaying lift after promo ends.",
    )

    compliance_pct = st.slider(
        "Compliance Rate",
        min_value=30, max_value=100, value=65, step=5,
        format="%d%%",
        help="Fraction of targeted customers who respond to the promotion.",
    )
    compliance_rate = compliance_pct / 100

    cashback_pct = st.slider(
        "Cashback Rate",
        min_value=1, max_value=10, value=3, step=1,
        format="%d%%",
        help="Cashback applied to treated spend during the promo window.",
    )
    cashback_rate = cashback_pct / 100

# -----------------------------------------------------------------------
# Calculations
# -----------------------------------------------------------------------
kpis = recalculate(margin, persistence_weeks, compliance_rate, cashback_rate)
base = baseline()

# -----------------------------------------------------------------------
# Title
# -----------------------------------------------------------------------
st.title("Cashback Promotion: Economic Viability Analysis")
st.caption(
    "Difference-in-Differences framework | 20,000 simulated customers | "
    "Mid-tier segment targeted ($125-$300/wk) | 4-week promotion window"
)

st.divider()

# -----------------------------------------------------------------------
# KPI cards
# -----------------------------------------------------------------------
st.subheader("Key Metrics")

col1, col2, col3, col4, col5, col6 = st.columns(6)

col1.metric(
    "Treated Customers",
    f"{TREATED_CUSTOMERS:,}",
)
col2.metric(
    "DiD Lift",
    f"${DID_LIFT:.2f}/wk",
    help="Per treated customer per week. Fixed simulation output.",
)
col3.metric(
    "Incremental Spend",
    f"${kpis['incremental_spend']:,.0f}",
    delta=f"${kpis['incremental_spend'] - base['incremental_spend']:,.0f} vs baseline",
)
col4.metric(
    "Cashback Cost",
    f"${kpis['cashback_cost']:,.0f}",
    delta=f"${kpis['cashback_cost'] - base['cashback_cost']:,.0f} vs baseline",
    delta_color="inverse",
)
col5.metric(
    "Net P&L",
    f"${kpis['net_profit']:,.0f}",
    delta=f"${kpis['net_profit'] - base['net_profit']:,.0f} vs baseline",
)
col6.metric(
    "Break-even Margin",
    f"{kpis['break_even_margin']:.1%}",
    delta=f"{(kpis['break_even_margin'] - base['break_even_margin']):.1%} vs baseline",
    delta_color="inverse",
)

st.divider()

# -----------------------------------------------------------------------
# Charts
# -----------------------------------------------------------------------
st.subheader("Behavioral Impact & Economic Sensitivity")
st.caption(
    "Persistence duration reflects slider input. "
    "Lift magnitude is held fixed -- the model does not encode cashback elasticity."
)

col_left, col_right = st.columns(2)

with col_left:
    figures_path = os.path.join(os.path.dirname(__file__), "outputs", "figures")
    panel_cache = os.path.join(figures_path, "df_panel.parquet")

    if os.path.exists(panel_cache):
        df_panel = pd.read_parquet(panel_cache)
        max_week = config.WEEKS_PRE + config.WEEKS_POST + persistence_weeks
        st.plotly_chart(
            plotly_normalized_segment_trends(df_panel, max_week=max_week),
            width="stretch",
        )
    else:
        st.image(
            os.path.join(figures_path, "normalized_segment_trends.png"),
            caption="Normalized Segment Trends (run main.py to enable interactive version)",
        )

with col_right:
    st.plotly_chart(
        plotly_margin_sensitivity(
            kpis["incremental_spend"],
            kpis["cashback_cost"],
            highlight_margin=margin,
        ),
        width="stretch",
    )

st.divider()

# -----------------------------------------------------------------------
# Recommendation block
# -----------------------------------------------------------------------
st.subheader("Business Recommendation")

be = kpis["break_even_margin"]
net = kpis["net_profit"]

if net > 0:
    st.success(
        f"At a {margin:.0%} revenue margin with {persistence_weeks}-week persistence "
        f"and {compliance_rate:.0%} compliance, the promotion generates a positive return "
        f"of **${net:,.0f}**. Current assumptions exceed the break-even margin of {be:.1%}."
    )
else:
    st.warning(
        f"At a {margin:.0%} revenue margin, the promotion does not break even "
        f"(net P&L: **${net:,.0f}**). "
        f"Break-even requires a revenue margin of approximately **{be:.1%}** -- "
        f"{(be - margin):.1%} above the current assumption. "
        f"Consider re-evaluating cashback rate, targeting criteria, or merchant co-funding."
    )

# Cashback lever note -- computed live from current inputs
if cashback_rate > 0.01:
    kpis_reduced = recalculate(margin, persistence_weeks, compliance_rate, cashback_rate - 0.01)
    be_reduced = kpis_reduced["break_even_margin"]
    be_delta = be - be_reduced
    st.info(
        f"**Key lever: cashback rate.** Of the four adjustable parameters, cashback rate has the "
        f"most direct impact on economics -- it scales promotional cost linearly. "
        f"At current inputs, reducing cashback rate by 1% (from {cashback_rate:.0%} to "
        f"{cashback_rate - 0.01:.0%}) would lower the break-even margin by "
        f"approximately **{be_delta:.1%}**, to **{be_reduced:.1%}**."
    )
else:
    st.info(
        "**Key lever: cashback rate.** Of the four adjustable parameters, cashback rate has the "
        "most direct impact on economics -- it scales promotional cost linearly. "
        "Cashback rate is currently at its minimum (1%)."
    )
