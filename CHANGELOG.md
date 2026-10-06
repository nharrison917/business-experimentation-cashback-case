# Changelog

## Resume Polish -- Ground-Truth Validation (2026-10-06)

### Added

- `src/validation.py` -- re-runs the simulation with identical seeds and the
  promotion switched off to recover the true causal lift. Finds the DiD
  estimate ($8.85) overstates the true lift ($5.91) by ~50%, and decomposes
  the bias into regression-to-mean drift ($1.97) and non-parallel trends in
  levels plus selection ($0.97). The exact identity
  `DiD = true lift + placebo DiD` is asserted on every run.
- `outputs/simulation_results.json` -- simulation outputs and validation
  results, written by `main.py` and committed so the dashboard runs on a
  fresh clone
- `tests/test_illustrative.py` -- unit tests for the dashboard financial layer
  and the validation decomposition
- `LICENSE` (MIT), `pytest.ini`
- README: Ground-Truth Validation section, setup instructions, two new
  limitations

### Changed

- `src/illustrative.py` reads fixed inputs from the results JSON instead of
  constants back-derived from rounded README figures. Treated customer count
  corrected from 7,956 to 7,948; baseline dashboard KPIs now match `main.py`
  exactly.
- `src/generate_data.py` -- effect parameters are overridable and a
  `simulate_panel()` wrapper replaces the inline sequence in `main.py`.
  Default outputs are unchanged.
- Mid-tier thresholds moved to `config.py` (`UPPER_WEEKLY_THRESHOLD` added)
- `config.py` comment on `REGRESSION_TO_MEAN` corrected: the drift applies to
  all treated customers, not only low spenders
- `requirements.txt` -- minimum versions pinned; `pyarrow` (used directly by
  `main.py`) and `pytest` added
- Dashboard DiD Lift tooltip notes the ground-truth lift
- CLAUDE.md brought up to date

---

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
- Static output charts (matplotlib PNGs)
