"""Load project tables by name.

    from shared.io import list_tables, load
    list_tables()
    df = load("some_table", columns=["a", "b"])
"""
import pandas as pd

from shared.config import PARQUET


def list_tables() -> list[str]:
    return sorted(p.stem for p in PARQUET.glob("*.parquet"))


def load(name: str, columns: list[str] | None = None) -> pd.DataFrame:
    path = PARQUET / f"{name}.parquet"
    if not path.exists():
        raise FileNotFoundError(f"{path} not found. Run shared.download then shared.convert. Have: {list_tables()}")
    return pd.read_parquet(path, columns=columns)
