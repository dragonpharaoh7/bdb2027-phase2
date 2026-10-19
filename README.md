# NFL Big Data Bowl 2027: Phase II Preliminary Exploration

Two preliminary ideas linking NFL Scouting Combine sensor tracking (10 Hz) to regular-season NFL performance.

Due: presentation 11/4, paper 11/8 by 5:00pm.

## Structure

- `idea1/` first idea (motivation, methods, results, discussion)
- `idea2/` second idea (same structure)
- `shared/` data loading and cleaning code used by both ideas
- `data/raw/` competition data from Kaggle (not tracked)
- `data/processed/` cleaned or derived data (not tracked)
- `figures/` exported plots

## Rubric (100 pts)

| Section | Points |
| --- | --- |
| Motivation | 10 |
| Methods | 30 |
| Results | 30 |
| Discussion | 20 |
| Professional presentation | 10 |

## Data

Kaggle: https://www.kaggle.com/competitions/nfl-big-data-bowl-2027

Download the data into `data/raw/`. It is gitignored.

## Reproducing

Python. Set up an environment and install dependencies:

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Data pipeline

Run from the repo root. Needs Kaggle credentials (`KAGGLE_USERNAME` and `KAGGLE_KEY`, or `~/.kaggle/kaggle.json`) and the competition rules accepted on kaggle.com.

```
python -m shared.download    # fetch and unzip into data/raw
python -m shared.inventory   # profile every CSV, writes data/processed/inventory.md
python -m shared.convert     # CSV to parquet in data/processed/parquet
```

In a notebook: `from shared.io import list_tables, load`.

Each idea folder holds a Jupyter notebook with the four required sections (Motivation, Methods, Results, Discussion).
