# CLAUDE.md — Cashback Experiment

## Project Status

Complete. Phase 1 (simulation + DiD analysis) and Phase 2 (Streamlit
dashboard) are both built; see CHANGELOG.md for history. The repo is
portfolio-facing, so README accuracy matters.

---

## Critical: The Illustrative Model Distinction

The DiD lift estimate (~$8.85/customer/week) is a fixed output of the simulation.
The dashboard does NOT re-run the simulation on slider change.

Sliders recalculate the financial layer only:

```
adjusted_lift     = did_lift * (compliance / 0.65)
incremental_spend = adjusted_lift * treated_customers * (4 + persistence_weeks)
cashback_cost     = cashback_rate * avg_treated_promo_spend * treated_customers * 4
net_profit        = (incremental_spend * margin) - cashback_cost
break_even_margin = cashback_cost / incremental_spend
```

This logic lives in `src/illustrative.py`, which reads its fixed inputs from
`outputs/simulation_results.json` (written by `main.py`). Do not hard-code
simulation outputs there. Do not propose re-running `generate_data.py` or
`analysis.py` in response to slider input.

---

## Ground-Truth Validation: the DiD Estimate Is Biased

`src/validation.py` re-simulates with the promotion off (same seeds) and shows
DiD overstates the true lift (~$8.85 vs ~$5.91). The bias comes from the
`REGRESSION_TO_MEAN` drift applied to all treated customers and from running
DiD in levels on a multiplicative trend. This is documented in the README as a
finding, deliberately. Do not "fix" the simulation to remove it without
discussing first -- README figures, PNGs, the results JSON and the dashboard
screenshot all depend on current outputs.

---

## Run Order Dependency

`main.py` generates `outputs/simulation_results.json` and the two PNGs in
`outputs/figures/`. All three are committed, so the dashboard runs on a fresh
clone. Running `main.py` also writes `outputs/figures/df_panel.parquet`
(ignored), which enables the interactive segment chart; without it the
dashboard falls back to the static PNG. After changing `config.py`, re-run
`main.py` and commit the regenerated outputs.

```bash
python main.py
streamlit run dashboard.py
```

---

## Two Chart Layers in `src/visuals.py`

The existing matplotlib functions (`plot_normalized_segment_trends`,
`plot_margin_sensitivity`) save static PNGs and are called by `main.py`.
Do not remove or modify them.

The Plotly equivalents (`plotly_normalized_segment_trends`,
`plotly_margin_sensitivity`) return `Figure` objects for the dashboard.
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

Do not simplify this pattern. A fifth line, `!outputs/simulation_results.json`,
works as a direct negation because the file sits directly under `outputs/`
(whose contents, not the directory itself, are ignored).
