"""Write a self-contained HTML viewer for one Combine drill.

    from shared.drill_viewer import align_reps, write_viewer
    reps = align_reps(ct, ol_ids)
    write_viewer(reps, 'PASS_PRO_MIRROR_DRILL', FIGURES / 'drill_review')

The page shows every rep top-down from its own start point, plays it back with a
speed trace, overlays the same player's other reps, and marks chosen times.
Open the file in any browser. No internet needed except for the font.
"""
import json
from pathlib import Path

import pandas as pd

TEMPLATE = Path(__file__).with_name("drill_viewer_template.html")
MARK_COLORS = ["--mark12", "--mark15"]


def align_reps(ct: pd.DataFrame, nfl_ids) -> pd.DataFrame:
    """Player rows for the given players, each rep shifted to start at (0, 0).

    Adds `t` (seconds from clip start), `dx`, `dy`, and `rep` (1, 2, ... in time order
    within player and drill; the raw `attempt` column is not 1 and 2).
    """
    d = ct[ct["entity_type"].eq("PLAYER") & ct["nfl_id"].isin(nfl_ids)]
    d = d.sort_values(["event_id", "time"]).copy()
    g = d.groupby("event_id")
    d["t"] = (pd.to_datetime(d["time"]) - pd.to_datetime(g["time"].transform("first"))).dt.total_seconds()
    d["dx"] = d["x"] - g["x"].transform("first")
    d["dy"] = d["y"] - g["y"].transform("first")
    start = d.groupby("event_id").agg(nfl_id=("nfl_id", "first"), drill_name=("drill_name", "first"),
                                      t0=("time", "first"))
    start["rep"] = start.sort_values("t0").groupby(["nfl_id", "drill_name"]).cumcount() + 1
    return d.merge(start[["rep"]], left_on="event_id", right_index=True)


def write_viewer(reps: pd.DataFrame, drill: str, out_dir, marks=(1.2, 1.5)) -> Path:
    """Write <out_dir>/<drill>.html and return its path. `marks` are times in seconds
    to circle on the path and draw on the speed trace (up to two)."""
    d = reps[reps["drill_name"].eq(drill)]
    if d.empty:
        raise ValueError(f"No reps for {drill!r}")
    n_reps = d.groupby("nfl_id")["event_id"].nunique()
    rows = []
    for e, r in d.groupby("event_id"):
        rows.append({
            "id": int(r["nfl_id"].iloc[0]), "yr": int(r["draft_year"].iloc[0]),
            "rep": int(r["rep"].iloc[0]), "n": int(n_reps[r["nfl_id"].iloc[0]]),
            "x": r["dx"].round(2).tolist(), "y": r["dy"].round(2).tolist(),
            "s": r["s_sg"].fillna(r["s"]).round(2).tolist(),
        })
    rows.sort(key=lambda r: (r["yr"], r["id"], r["rep"]))

    marks = list(marks)[:2]
    mark_js = json.dumps([[m, c] for m, c in zip(marks, MARK_COLORS)])
    legend = "\n".join(
        f'        <span><i class="sw" style="background:var({c})"></i>{m} s</span>'
        for m, c in zip(marks, MARK_COLORS))
    meta = (f"{n_reps.size} players, {len(rows)} reps "
            f"({len(rows) / n_reps.size:.2f} per player).")

    html = (TEMPLATE.read_text(encoding="utf-8")
            .replace("__DRILL__", drill)
            .replace("__META__", meta)
            .replace("__MARKS__", mark_js)
            .replace("__MARKLEGEND__", legend)
            .replace("__DATA__", json.dumps(rows, separators=(",", ":"))))
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{drill}.html"
    path.write_text(html, encoding="utf-8")
    return path
