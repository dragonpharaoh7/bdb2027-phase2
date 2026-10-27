"""Fixes for known data quirks. Each function does one thing and returns a new frame.

Known quirks (checked on the raw parquet files, October 2026):
1. Combine `dis` is wrong. Rebuild step distance from x and y.
2. Combine `a` is unsigned. Derive signed acceleration from the change in `s`.
3. Game `a` is unsigned in 2023 and 2024 but has negatives in 2025. Use the same
   signed acceleration from `s` for every season so they match.
4. Some drills were renamed between classes. Map them to one name.
5. Text "NA" may stand in for missing values. Turn it into real nulls.
6. Game plays run both directions. Flip so the offense always moves toward +x.

Added for 01_preprocess (runs on 00's clean output):
7. Combine clips mix BALL rows into the same event_id (551 clips). Kinematics must be
   grouped by event_id and entity_type, or ball and player get stitched together.
8. Raw frame-to-frame acceleration is noisy. smooth_kinematics adds Savitzky-Golay
   speed and acceleration (s_sg, a_sg) within each clip or play.
9. Rare tracking dropouts (player teleports or speed drops to 0 for a frame, about
   0.2% of game tracks). flag_glitches marks them; drop those tracks before features.
"""
import numpy as np
import pandas as pd
from scipy.signal import savgol_filter

HZ = 10  # frames per second, both feeds
SG_WINDOW = 7  # frames (0.7 s); odd number
SG_ORDER = 2   # polynomial order

# 4. one name per drill across classes
DRILL_RENAMES = {
    "LINE": "LINE_DRILL",
    "PASS_PRO-MIRROR_DRILL": "PASS_PRO_MIRROR_DRILL",
    "OVER_THE_SHOULDER_ADJUST": "OVER_SHOULDER_ADJUST",
    "SPEED_OUT_LEFT": "SPEED_OUT_ROUTE_LEFT",
}
# Left as is on purpose: DL SHORT_ZONE_BREAKS (2023-24) vs three 2025 variants,
# because the 2025 split may be a different drill, not just a new name.


def na_to_null(df: pd.DataFrame) -> pd.DataFrame:
    """5. Replace text 'NA' with real nulls in text columns."""
    out = df.copy()
    for c in out.columns:
        if out[c].dtype == object or str(out[c].dtype).startswith("str"):
            out[c] = out[c].replace({"NA": np.nan, "": np.nan})
    return out


def harmonize_drills(ct: pd.DataFrame) -> pd.DataFrame:
    """4. Apply DRILL_RENAMES."""
    out = ct.copy()
    out["drill_name"] = out["drill_name"].replace(DRILL_RENAMES)
    return out


def add_kinematics(df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    """1-3. Step distance from x/y and signed acceleration from s, within each clip or play.

    Adds `step_dist` (yd) and `a_signed` (yd/s^2). Leaves the original columns untouched.
    The first frame of each group gets NaN.
    """
    out = df.sort_values(group_cols + ["time"]).copy()
    g = out.groupby(group_cols, sort=False)
    dx = g["x"].diff()
    dy = g["y"].diff()
    out["step_dist"] = np.hypot(dx, dy)
    out["a_signed"] = g["s"].diff() * HZ
    return out


def standardize_direction(game: pd.DataFrame, play_dir: pd.DataFrame) -> pd.DataFrame:
    """6. Flip plays moving left so the offense always moves toward +x.

    `play_dir` needs game_id, play_id, play_direction (from player_play).
    Field is 120 x 53.3 yd. Angles `o` and `dir` are rotated 180 degrees on flipped plays.
    """
    pdir = play_dir[["game_id", "play_id", "play_direction"]].drop_duplicates()
    out = game.merge(pdir, on=["game_id", "play_id"], how="left")
    left = out["play_direction"].eq("left")
    out.loc[left, "x"] = 120 - out.loc[left, "x"]
    out.loc[left, "y"] = 160 / 3 - out.loc[left, "y"]
    for ang in ("o", "dir"):
        if ang in out:
            out.loc[left, ang] = (out.loc[left, ang] + 180) % 360
    return out


def _sg(s: pd.Series, window: int, order: int, deriv: int) -> np.ndarray:
    """Savitzky-Golay on one clip or play. Too-short groups come back as NaN."""
    v = s.to_numpy(dtype=float)
    if len(v) < window or np.isnan(v).any():
        return np.full(len(v), np.nan)
    return savgol_filter(v, window, order, deriv=deriv, delta=1 / HZ, mode="interp")


def smooth_kinematics(df: pd.DataFrame, group_cols: list[str],
                      window: int = SG_WINDOW, order: int = SG_ORDER) -> pd.DataFrame:
    """8. Add `s_sg` (smoothed speed, yd/s) and `a_sg` (smoothed signed acceleration,
    yd/s^2) within each clip or play. Use a_sg for features; a_signed is raw.
    """
    out = df.sort_values(group_cols + ["time"]).copy()
    g = out.groupby(group_cols, sort=False)["s"]
    out["s_sg"] = g.transform(lambda s: _sg(s, window, order, 0))
    out["a_sg"] = g.transform(lambda s: _sg(s, window, order, 1))
    return out


def flag_glitches(df: pd.DataFrame, group_cols: list[str],
                  max_step: float = 1.5, max_a: float = 15.0) -> pd.DataFrame:
    """9. Flag a one-frame jump over `max_step` yd (15 yd/s) or a raw speed change over
    `max_a` yd/s^2. Adds `glitch_frame`, and `glitch_track` for every frame of a clip or
    play that has one. Needs step_dist and a_signed from add_kinematics.
    """
    out = df.copy()
    out["glitch_frame"] = out["step_dist"].gt(max_step) | out["a_signed"].abs().gt(max_a)
    out["glitch_track"] = out.groupby(group_cols, sort=False)["glitch_frame"].transform("any")
    return out


def check_direction(game: pd.DataFrame, plays: pd.DataFrame, secs: float = 1.5) -> pd.Series:
    """6. Check the flip. On pass plays, receivers running a route should gain x in the
    first `secs` after the snap, and pass-blocking players should lose x.
    Returns the share of player-plays moving the expected way.
    """
    keys = ["game_id", "play_id", "nfl_id"]
    pp_ = plays[keys + ["route_ran", "pass_rushers_encountered"]]
    snap = (game[game["event"].eq("ball_snap")]
            .groupby(["game_id", "play_id"])["time"].min().rename("snap_time"))
    g = game[keys + ["time", "x"]].merge(snap, on=["game_id", "play_id"])
    dt = (pd.to_datetime(g["time"]) - pd.to_datetime(g["snap_time"])).dt.total_seconds()
    x0 = g[dt.between(-0.05, 0.05)].groupby(keys)["x"].first()
    x1 = g[dt.between(secs - 0.05, secs + 0.05)].groupby(keys)["x"].first()
    d = (x1 - x0).rename("dx").reset_index().merge(pp_, on=keys)
    route = d[d["route_ran"].notna()]
    block = d[d["pass_rushers_encountered"].notna() & d["route_ran"].isna()]
    return pd.Series({
        "route runners gaining x": (route["dx"] > 0).mean(),
        "n route runners": len(route),
        "pass blockers losing x": (block["dx"] < 0).mean(),
        "n pass blockers": len(block),
    })
