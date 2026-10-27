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

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Then authenticate to Kaggle once with OAuth:

```powershell
.\.venv\Scripts\python.exe -m kaggle auth login
```

That opens a browser, then caches credentials in `~/.kaggle/credentials.json`
and refreshes them on its own. Nothing secret lands in the repo.

If you would rather not use OAuth, copy `.env.example` to `.env` and paste a
token from kaggle.com/settings/api into `KAGGLE_API_TOKEN` instead. `.env` is
gitignored and `shared/config.py` loads it automatically.

## Data pipeline

Run from the repo root. Needs the Kaggle login above and the competition rules accepted on kaggle.com.

```
python -m shared.download    # fetch and unzip into data/raw
python -m shared.inventory   # profile every CSV, writes data/processed/inventory.md
python -m shared.convert     # CSV to parquet in data/processed/parquet
```

Then `python -m shared.overlap` prints the Combine-to-game tracking overlap by
position group.

In a notebook: `from shared.io import list_tables, load`. Short table names
work, so `load("players")` resolves the full parquet name.

## Data overview

`data_overview.ipynb` at the repo root profiles all nine tables, confirms the
10 Hz frame rate, and settles the Combine-to-game overlap. Run it after the
pipeline above. It is description only, no idea selection and no modeling.

Each idea folder holds a Jupyter notebook with the four required sections (Motivation, Methods, Results, Discussion).
