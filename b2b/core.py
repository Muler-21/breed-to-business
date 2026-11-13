"""Core linear-model tools: dummy coding and sequential (Type I) ANOVA by least squares.

Only numpy, pandas and scipy are needed, so the code runs on any laptop
without extra statistics packages.
"""
import numpy as np
import pandas as pd
from scipy import stats


def dummies(values, drop_first=True):
    """0/1 indicator matrix for a categorical vector."""
    cats = pd.Categorical(values)
    m = np.eye(len(cats.categories))[cats.codes]
    return m[:, 1:] if drop_first else m


def interaction(a, b):
    """Label for every combination of two factors, e.g. genotype x environment."""
    return pd.Series(a).astype(str).str.cat(pd.Series(b).astype(str), sep=":").values


def _fit(X, y):
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    return float(resid @ resid), int(np.linalg.matrix_rank(X)), beta


def seq_anova(y, terms):
    """Sequential (Type I) ANOVA.

    terms: list of (name, matrix) added in order after the intercept.
    The last term is adjusted for every term before it, so put the effect
    you want to test fairly (e.g. genotype after blocks) last or test it
    in a second ordering.
    Returns a DataFrame with Source, df, SS, MS (F and p against the residual).
    """
    y = np.asarray(y, float)
    n = len(y)
    X = np.ones((n, 1))
    rss_prev, rank_prev, _ = _fit(X, y)
    rows = []
    for name, M in terms:
        X = np.hstack([X, M])
        rss, rank, _ = _fit(X, y)
        rows.append([name, rank - rank_prev, rss_prev - rss])
        rss_prev, rank_prev = rss, rank
    df_e = n - rank_prev
    rows.append(["Residual", df_e, rss_prev])
    t = pd.DataFrame(rows, columns=["Source", "df", "SS"])
    t["MS"] = t["SS"] / t["df"].replace(0, np.nan)
    mse = t["MS"].iloc[-1]
    t["F"] = t["MS"] / mse
    t["p"] = [stats.f.sf(f, d, df_e) if d > 0 else np.nan for f, d in zip(t["F"], t["df"])]
    t.loc[t.index[-1], ["F", "p"]] = np.nan
    return t


def f_test(ms_num, df_num, ms_den, df_den):
    f = ms_num / ms_den
    return f, stats.f.sf(f, df_num, df_den)


def stars(p):
    if p is None or np.isnan(p):
        return ""
    return "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"


def tukey_hsd(means, n_per_group, mse, df_e, alpha=0.05):
    """Tukey HSD letters for treatment means (equal n). Returns dict name -> letters."""
    names = list(means.index)
    q = stats.studentized_range.ppf(1 - alpha, len(names), df_e)
    hsd = q * np.sqrt(mse / n_per_group)
    order = means.sort_values(ascending=False).index.tolist()
    groups = []
    for i, a in enumerate(order):
        grp = [b for b in order[i:] if means[a] - means[b] <= hsd]
        if not any(set(grp) <= set(g) for g in groups):
            groups.append(grp)
    letters = {n: "" for n in names}
    for k, g in enumerate(groups):
        for n in g:
            letters[n] += "abcdefghijklmnopqrstuvwxyz"[k]
    return letters, hsd
