"""Reliability helpers. Each function is small on purpose so the math is easy to check.

icc21(a, b)       ICC(2,1), two-way random, absolute agreement, single measure.
                  a and b are the same players measured twice (e.g. left rep, right rep).
spearman_brown(r, k)  reliability of the average of k measures given single-measure r.
split_half(df, id_col, cols, n_splits, seed)
                  random split of each player's rows into halves, correlate the half
                  means across players, Spearman-Brown up to full length, average over splits.
"""
import numpy as np
import pandas as pd


def icc21(a, b) -> float:
    x = np.column_stack([a, b]).astype(float)
    x = x[~np.isnan(x).any(axis=1)]
    n, k = x.shape
    gm = x.mean()
    ms_rows = k * ((x.mean(axis=1) - gm) ** 2).sum() / (n - 1)
    ms_cols = n * ((x.mean(axis=0) - gm) ** 2).sum() / (k - 1)
    resid = x - x.mean(axis=1, keepdims=True) - x.mean(axis=0, keepdims=True) + gm
    ms_err = (resid ** 2).sum() / ((n - 1) * (k - 1))
    return (ms_rows - ms_err) / (ms_rows + (k - 1) * ms_err + k * (ms_cols - ms_err) / n)


def spearman_brown(r: float, k: float) -> float:
    return k * r / (1 + (k - 1) * r)


def split_half(df: pd.DataFrame, id_col: str, cols: list[str],
               n_splits: int = 50, seed: int = 0) -> pd.Series:
    rng = np.random.default_rng(seed)
    out = {c: [] for c in cols}
    for _ in range(n_splits):
        half = rng.random(len(df)) < 0.5
        a = df[half].groupby(id_col)[cols].mean()
        b = df[~half].groupby(id_col)[cols].mean().loc[a.index]
        for c in cols:
            out[c].append(spearman_brown(np.corrcoef(a[c], b[c])[0, 1], 2))
    return pd.Series({c: float(np.mean(v)) for c, v in out.items()})
