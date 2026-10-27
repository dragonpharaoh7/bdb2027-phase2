"""Paths and constants shared across the project."""
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # dotenv is optional, env vars may be set another way
    load_dotenv = None

COMPETITION = "nfl-big-data-bowl-2027"

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
PARQUET = PROCESSED / "parquet"
FIGURES = ROOT / "figures"

ENV_FILE = ROOT / ".env"

for _p in (RAW, PROCESSED, PARQUET, FIGURES):
    _p.mkdir(parents=True, exist_ok=True)

# Load .env so the Kaggle CLI sees KAGGLE_USERNAME and KAGGLE_KEY. Existing
# environment variables win, so a shell export overrides the file.
if load_dotenv is not None and ENV_FILE.exists():
    load_dotenv(ENV_FILE, override=False)
