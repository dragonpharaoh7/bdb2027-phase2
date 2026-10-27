"""Load project tables by name.

    from shared.io import list_tables, load
    list_tables()
    df = load("players", columns=["nfl_id", "nfl_position"])

The converter prefixes each parquet file with the zip's folder name, e.g.
``nfl-big-data-bowl-2027__players``. Short names are resolved against that, so
``load("players")`` works as long as the short name is unambiguous.
"""
import pandas as pd

from shared.config import PARQUET


def list_tables() -> list[str]:
    return sorted(p.stem for p in PARQUET.glob("*.parquet"))


def resolve(name: str) -> str:
    """Map a short table name onto a full parquet stem."""
    tables = list_tables()
    if name in tables:
        return name
    matches = [t for t in tables if t.split("__")[-1] == name]
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise FileNotFoundError(
            f"No table named {name!r}. Run shared.download then shared.convert. Have: {tables}"
        )
    raise ValueError(f"{name!r} is ambiguous, matches {matches}. Use the full name.")


def load(name: str, columns: list[str] | None = None) -> pd.DataFrame:
    return pd.read_parquet(PARQUET / f"{resolve(name)}.parquet", columns=columns)
