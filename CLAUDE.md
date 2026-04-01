# CLAUDE.md — Cashback Experiment

## Project Status

Two-phase project. Phase 1 (simulation + DiD analysis) is complete.
Phase 2 (Streamlit dashboard) is planned in PHASE_TWO.md and not yet built.

---

## Critical: The Illustrative Model Distinction

The DiD lift estimate (~$8.85/customer/week) is a fixed output of the simulation.
The dashboard does NOT re-run the simulation on slider change.

Sliders recalculate the financial layer only:

```
incremental_spend = lift * compliant_customers * sum(decay_weights)
cashback_cost     = cashback_rate * total_treated_spend
net_profit        = (incremental_spend * margin) - cashback_cost
break_even_margin = cashback_cost / incremental_spend
```

This logic will live in `src/illustrative.py`. Do not propose re-running
`generate_data.py` or `analysis.py` in response to slider input.

---

## Run Order Dependency

On a fresh clone, `main.py` must be run before `dashboard.py`.
`main.py` generates `outputs/figures/normalized_segment_trends.png` and
`outputs/figures/margin_sensitivity.png`, which the dashboard uses.

```bash
python main.py
streamlit run dashboard.py
```

---

## Two Chart Layers in `src/visuals.py`

The existing matplotlib functions (`plot_normalized_segment_trends`,
`plot_margin_sensitivity`) save static PNGs and are called by `main.py`.
Do not remove or modify them.

Phase 2 will add Plotly equivalents (`plotly_normalized_segment_trends`,
`plotly_margin_sensitivity`) that return `Figure` objects for the dashboard.
These coexist in the same file — that is intentional.

---

## `.gitignore` Pattern for Figures

The figures directory is inside an otherwise-ignored `outputs/` directory.
Simple negation (`!outputs/figures/*.png`) silently fails when the parent
is ignored. The correct four-line pattern is:

```
outputs/*
!outputs/figures/
outputs/figures/*
!outputs/figures/*.png
```

Do not simplify this pattern.
