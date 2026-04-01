# Phase Two: Interactive Dashboard

## Goal

Add a single-page Streamlit dashboard that surfaces the KPIs from the existing
analysis and lets a user stress-test the financial assumptions via sliders. The
output is a conditional business recommendation that updates live.

---

## Architectural Decisions (locked)

| Decision | Choice | Rationale |
|---|---|---|
| Layout | Single page | Analysis and decision tool are one continuous argument |
| Slider placement | Sidebar | Always visible; all four sliders feed the recommendation block simultaneously |
| Interactivity model | Illustrative | DiD lift held fixed; only the financial layer recalculates on slider change |
| Chart library | Plotly via `st.plotly_chart()` | Interactive; consistent with project output standards |
| Code coupling | Import `src/` directly | Avoids duplicating logic; `src/` is stable |
| Deployment | Local only | Portfolio piece; README provides context |

---

## Illustrative Model — Core Logic

The DiD estimate is treated as a fixed input. Sliders recalculate the financial
layer only:

```
incremental_spend = lift_per_customer * compliant_customers * sum(decay_weights)
cashback_cost     = cashback_rate * total_treated_spend
net_profit        = (incremental_spend * margin) - cashback_cost
break_even_margin = cashback_cost / incremental_spend
```

Where:
- `compliant_customers = treated_customers * compliance_rate`
- `decay_weights` = per-week contribution over persistence duration (mirrors
  existing decay curve in the simulation)
- `total_treated_spend` = baseline treated spend + incremental_spend

Caveat displayed in UI: "Behavioral lift estimate held fixed at DiD result.
Sliders adjust financial assumptions only."

---

## Page Structure

### Sidebar
Four sliders with default values matching the original simulation:

| Slider | Min | Max | Default |
|---|---|---|---|
| Revenue Margin | 1% | 20% | 6% |
| Behavioral Persistence (weeks) | 8 | 32 | 20 |
| Compliance Rate | 30% | 100% | 65% |
| Cashback Rate | 1% | 10% | 3% |

### Section 1 — Header
- Title + one-line description
- Caveat caption

### Section 2 — KPI Cards (`st.columns(6)`)
| Card | Value source |
|---|---|
| Treated Customers | From simulation (fixed) |
| DiD Lift ($/wk) | From DiD result (fixed) |
| Incremental Spend | Recalculated |
| Cashback Cost | Recalculated |
| Net P&L | Recalculated |
| Break-even Margin | Recalculated |

KPI cards use `st.metric()` with delta indicators vs. baseline where applicable.

### Section 3 — Charts (`st.columns(2)`)
- Left: Normalized segment trends (behavioral — does not change with sliders)
- Right: Margin sensitivity curve (recalculated — updates with slider changes)

Both built as Plotly figures.

### Section 4 — Recommendation Block
Conditional text driven by whether `net_profit > 0` at current slider state:

- **Viable:** `st.success()` — "At X% margin and Y-week persistence, the
  promotion generates positive returns of $Z."
- **Not viable:** `st.warning()` — "At X% margin, the promotion does not break
  even. Break-even requires a margin of approximately Y%."

In both cases, append: "Sensitivity note: [which assumption is the binding
constraint at current values]."

---

## Files to Create or Modify

### New: `dashboard.py` (project root)
Main Streamlit app. Imports from `src/`. Contains all layout and slider logic.

### New: `src/illustrative.py`
Single function `recalculate(margin, persistence_weeks, compliance_rate,
cashback_rate)` that returns a dict of KPIs. Keeps dashboard.py thin.

### Modify: `src/visuals.py`
Add two new functions returning Plotly `Figure` objects (not saving to disk):
- `plotly_normalized_segment_trends(df_panel)` 
- `plotly_margin_sensitivity(incremental_spend, cashback_cost, highlight_margin)`

The existing matplotlib functions stay untouched (used by `main.py`).

### Modify: `requirements.txt`
Already updated: added `streamlit`, `plotly`.

---

## Implementation Order

1. `src/illustrative.py` — recalculation function + tests against known values
2. `src/visuals.py` — add two Plotly figure functions
3. `dashboard.py` — wire layout, sliders, KPI cards, charts, recommendation block
4. Smoke test: run `main.py` to confirm existing pipeline unaffected
5. Run dashboard: `streamlit run dashboard.py`

---

## Out of Scope

- Re-running the simulation on slider change
- Streamlit Community Cloud deployment
- Additional pages or navigation
- Persisting slider state between sessions
