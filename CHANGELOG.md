# Changelog

## Phase 2 -- Interactive Dashboard (2026-04-01)

### Added

- `dashboard.py` -- single-page Streamlit dashboard with sidebar assumption controls
- `src/illustrative.py` -- financial recalculation layer; holds DiD lift fixed and
  recomputes KPIs from slider inputs without re-running the simulation
- Plotly chart functions in `src/visuals.py`:
  - `plotly_normalized_segment_trends()` -- interactive spend index chart;
    truncates at persistence slider value
  - `plotly_margin_sensitivity()` -- interactive profit curve with live
    break-even marker at current margin setting

### Dashboard features

- Six KPI cards with delta indicators vs. baseline assumptions
- Four sidebar sliders: revenue margin, behavioral persistence, compliance rate,
  cashback rate
- Conditional recommendation block (st.success / st.warning) driven by net P&L
- Cashback lever note: computes live impact of a 1% cashback rate reduction on
  break-even margin
- Inline limitation caption: distinguishes which chart elements respond to sliders
  and which are held fixed

### Modified

- `main.py` -- saves `df_panel.parquet` to `outputs/figures/` to enable
  interactive Plotly chart in dashboard (falls back to static PNG if absent)
- `src/visuals.py` -- added `max_week` parameter to
  `plotly_normalized_segment_trends()` for persistence slider truncation
- `requirements.txt` -- added `streamlit`, `plotly`
- `README.md` -- added dashboard section, limitations section, updated
  project structure and how-to-run instructions

### Design decisions

- Illustrative (not simulation-based) interactivity: slider changes recalculate
  the financial layer only. DiD lift (~$8.85/customer/week) is a fixed simulation
  output. This avoids presenting made-up behavioral elasticities as analytical results.
- Cashback rate is identified as the primary economic lever: it scales promotional
  cost linearly, unlike the other parameters which affect the revenue side with
  diminishing returns.
- Behavioral lift is treated as invariant to cashback rate by design. Encoding
  cashback elasticity would require an empirical estimate not available from this
  simulation.

---

## Phase 1 -- Simulation and Analysis (initial commit)

- Simulated 20,000 customers with right-skewed baseline spend distribution
- Deterministic mid-tier segment targeting ($125-$300/wk)
- Difference-in-Differences regression with HC3 robust standard errors
- Financial evaluation: incremental revenue vs. cashback cost
- Margin sensitivity analysis; break-even margin ~12%
- Static Plotly-style output charts via matplotlib
