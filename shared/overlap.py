"""Which players have BOTH Combine tracking and NFL game tracking.

That overlap is what decides whether an idea is feasible, so it lives here
rather than in a notebook. Column names below were read off
data/processed/inventory.md, not assumed.

    python -m shared.overlap
"""
import pandas as pd

from shared.io import list_tables, load

# Shared player key across every table in this release.
KEY = "nfl_id"
GAME_TRACKING_SEASONS = (2023, 2024, 2025)


def game_tracking_seasons() -> list[int]:
    """Season suffixes of the game_tracking tables actually present."""
    found = []
    for t in list_tables():
        short = t.split("__")[-1]
        if short.startswith("game_tracking_"):
            found.append(int(short.rsplit("_", 1)[-1]))
    return sorted(found)


def combine_tracking_ids() -> set:
    """Players with at least one Combine tracking row.

    entity_type is filtered to PLAYER because the file also carries BALL rows.
    """
    ct = load("combine_tracking", columns=[KEY, "entity_type"])
    return set(ct.loc[ct["entity_type"] == "PLAYER", KEY].unique())


def game_tracking_ids(by_season: bool = False):
    """Players with at least one game tracking row."""
    per = {yr: set(load(f"game_tracking_{yr}", columns=[KEY])[KEY].unique())
           for yr in game_tracking_seasons()}
    if by_season:
        return per
    return set().union(*per.values()) if per else set()


def player_flags() -> pd.DataFrame:
    """One row per player with has_combine_tracking / has_game_tracking / has_both."""
    players = load("players", columns=[KEY, "display_name", "nfl_position", "draft_year"])
    combine = load("combine_results", columns=[KEY, "combine_position"])
    df = players.merge(combine, on=KEY, how="left")

    ct_ids = combine_tracking_ids()
    per_season = game_tracking_ids(by_season=True)
    all_game = set().union(*per_season.values()) if per_season else set()

    df["has_combine_tracking"] = df[KEY].isin(ct_ids)
    df["has_game_tracking"] = df[KEY].isin(all_game)
    df["has_both"] = df["has_combine_tracking"] & df["has_game_tracking"]
    for yr, ids in per_season.items():
        df[f"game_tracking_{yr}"] = df[KEY].isin(ids)
    return df


def overlap_table(by: str = "combine_position", flags: pd.DataFrame | None = None) -> pd.DataFrame:
    """Counts of players with both feeds, grouped by a position column.

    `by` is "combine_position" (5 groups, from combine_results) or
    "nfl_position" (17 labels, from players).
    """
    df = player_flags() if flags is None else flags
    out = (df.groupby(by)
             .agg(players=(KEY, "size"),
                  combine_tracking=("has_combine_tracking", "sum"),
                  game_tracking=("has_game_tracking", "sum"),
                  both=("has_both", "sum")))
    out["pct_both"] = (100 * out["both"] / out["players"]).round(1)
    return out.sort_values("both", ascending=False)


def main() -> None:
    flags = player_flags()
    for col in ("combine_position", "nfl_position"):
        print(f"\n=== overlap by {col} ===")
        print(overlap_table(col, flags=flags).to_string())
    n = int(flags["has_both"].sum())
    print(f"\n{n} of {len(flags)} players have both Combine and game tracking.")


if __name__ == "__main__":
    main()
