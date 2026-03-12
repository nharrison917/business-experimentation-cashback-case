import pandas as pd
import statsmodels.formula.api as smf


def baseline_diagnostics(df_panel, verbose=True):
    """
    Compare average pre-period spend between treated and control groups.
    """

    df_pre = df_panel.loc[df_panel["period"] == "pre"]

    summary = (
        df_pre.groupby("treated", as_index=False)["spend"]
        .mean()
    )

    if verbose:
        print("\n=== Baseline Pre-Period Spend ===")
        print(summary)

    return summary


def naive_post_comparison(df_panel, verbose=True):
    """
    Compare average post-period spend between treated and control groups.
    """

    df_post = df_panel.loc[df_panel["period"] == "post"]

    summary = (
        df_post.groupby("treated", as_index=False)["spend"]
        .mean()
    )

    if verbose:
        print("\n=== Naive Post-Period Comparison ===")
        print(summary)

    return summary


def difference_in_differences(df_panel):
    """
    Run Difference-in-Differences regression:

        spend ~ treated + post + treated:post

    Uses heteroskedasticity-robust (HC3) standard errors.
    """

    df_panel = df_panel.copy()
    df_panel["post"] = (df_panel["period"] == "post").astype(int)

    model = smf.ols(
        "spend ~ treated + post + treated:post",
        data=df_panel
    ).fit(cov_type="HC3")

    return model