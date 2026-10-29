"""Route phase features, shared by game plays and Combine route drills.

Each function takes one route (rows in time order, `t` in seconds from the start,
smoothed speed `s_sg`, acceleration `a_sg`, `heading` in degrees) and returns numbers.
"""
import numpy as np
import pandas as pd

BREAK_ROUTES = {"HITCH", "IN", "OUT", "SLANT", "POST", "CORNER", "CROSS"}


def launch(r: pd.DataFrame) -> dict:
    """Peak acceleration in the first 1.0 s and speed at 1.0 s."""
    first = r[r["t"].between(0, 1.0)]
    at1 = r.loc[r["t"].sub(1.0).abs().idxmin(), "s_sg"]
    return {"launch_accel": first["a_sg"].max(), "speed_1s": at1}


def find_break(r: pd.DataFrame, t_from: float = 0.5, t_to: float | None = None, span: float = 0.8):
    """Start time of the `span`-second window with the largest heading change between
    t_from and t_to. Returns (t_break, heading_change_degrees) or (nan, nan)."""
    if t_to is None:
        t_to = r["t"].max()
    w = r[r["t"].between(t_from, t_to)].reset_index(drop=True)
    k = int(round(span * 10))
    if len(w) <= k:
        return np.nan, np.nan
    h = np.unwrap(np.radians(w["heading"].to_numpy()))
    change = np.abs(h[k:] - h[:-k])
    i = int(np.argmax(change))
    return float(w.loc[i, "t"]), float(np.degrees(change[i]))


def break_features(r: pd.DataFrame, t_to: float | None = None, span: float = 0.8) -> dict:
    """Entry speed (mean speed in the 0.5 s before the break), speed retention through
    the break (min speed in the break span / entry speed), and peak re-acceleration in
    the 0.7 s after it."""
    tb, turn = find_break(r, t_to=t_to, span=span)
    if np.isnan(tb):
        return {"entry_speed": np.nan, "break_retention": np.nan, "reaccel": np.nan,
                "break_t": np.nan, "turn_deg": np.nan}
    before = r[r["t"].between(tb - 0.5, tb - 0.05)]["s_sg"].mean()
    during = r[r["t"].between(tb, tb + span)]["s_sg"].min()
    after = r[r["t"].between(tb + span, tb + span + 0.7)]["a_sg"].max()
    return {"entry_speed": before, "break_retention": during / before if before > 0.5 else np.nan,
            "reaccel": after, "break_t": tb, "turn_deg": turn}
