"""Paths and constants shared across the project."""
from pathlib import Path

COMPETITION = "nfl-big-data-bowl-2027"

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
PARQUET = PROCESSED / "parquet"
FIGURES = ROOT / "figures"

for _p in (RAW, PROCESSED, PARQUET, FIGURES):
    _p.mkdir(parents=True, exist_ok=True)
