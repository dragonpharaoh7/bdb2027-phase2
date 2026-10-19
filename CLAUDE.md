# BDB 2027 Phase II

Graduate course project (IU Indianapolis, sports analytics master's, Logan Johnson). Python, not R, even though the course standard is R. The instructor's concepts guide has R snippets, so translate them to pandas and numpy.

## Assignment
Two-Idea Brief: two distinct preliminary ideas for the 2027 NFL Big Data Bowl. Logan is choosing the two ideas himself. Do not pick them for him, but do help test feasibility when asked. Each idea uses four sections with these points:
- Motivation (10): the football or analytics question, data sources and why they fit, value to coaches, front office or player development.
- Methods (30): data accessed, cleaning and filtering, metrics or models, exploratory visuals, derived variables, reproducible code.
- Results (30): early findings in text or visuals, patterns observed, how results tie back to the motivation.
- Discussion (20): limitations (data quality, sample size, confounding), feasibility for a full submission (expand, refine, or ditch), suggested collaborations.
- Professional presentation (10): organized layout, clear writing, consistent visuals, citations of data and code sources, ready to share with classmates.
Deliverable: one notebook (preferred, Jupyter) or two documents containing both ideas, plus supporting code the instructor can open. Presentation in class 11/4, paper due 11/8 by 5pm (the assignment text is garbled, confirm with the instructor). Failed ideas are explicitly fine if limitations are honest. Submissions are shared with the class to spark collaboration.

## Competition facts (Kaggle nfl-big-data-bowl-2027)
Theme: link 10 Hz NFL Combine sensor tracking to regular-season NFL game tracking. Final deadline Jan 6, 2027. Writeups: max 2,000 words, under 10 figures or tables, public Kaggle Notebook required, most code in an appendix. Anything not using tracking data is not scored. Required to explicitly link Combine tracking to regular-season performance. Scoring: football 30%, data science 30%, writeup 20%, visualization 20%. Judges are NFL team analytics staff and tracking vendors. Judges favor one narrow question (one drill, one position group, or one small aspect of movement) over broad evaluation. Official examples: route running and coverage (change of direction, deceleration into breaks, acceleration out of cuts vs separation), trench play (first step, lateral agility, burst vs pass rush or run blocking), drill translation (sensor metrics vs traditional drill times), position-specific mechanics vs rookie performance.

## Repo layout
- shared/config.py: paths (RAW, PROCESSED, PARQUET, FIGURES)
- shared/download.py: python -m shared.download, fetches the competition zip with the Kaggle CLI into data/raw. Needs KAGGLE_USERNAME and KAGGLE_KEY env vars or ~/.kaggle/kaggle.json.
- shared/inventory.py: python -m shared.inventory, profiles every CSV (rows, dtypes, null %, distinct counts, sample rows) into data/processed/inventory.md
- shared/convert.py: python -m shared.convert, chunked CSV to parquet in data/processed/parquet
- shared/io.py: list_tables() and load(name, columns=None)
- idea1/, idea2/: one folder per idea, notebooks go here
- data/raw and data/processed are gitignored. figures/ holds exported plots.
Run everything from the repo root. Windows machine, PowerShell.

## Status
Scaffold and schema-agnostic pipeline are written and were tested only on synthetic data. The real competition data has NOT been profiled. Do not assume column names, file names, units, coordinate conventions or frame rates. Read inventory.md first. Next steps: run download, inventory and convert. Then count how many players have BOTH Combine tracking and NFL game tracking, by position group. That overlap decides which ideas are feasible. Then write the join and cleaning code in shared/.

## Instructor concepts guide (summary, translate R to Python)
- Movement: Euclidean distance, displacement, distance traveled (sum of step lengths), speed, velocity components, acceleration, vector magnitude, centroid.
- Relationships: relative position and velocity, closing speed, dot product, cosine similarity, angle between vectors, bearing, nearest neighbor, mean pairwise distance.
- Time and pursuit: time to contact, time to target, projected position (constant velocity and acceleration-adjusted), path efficiency, excess path distance, reaction time.
- Trajectories: mean and RMSE trajectory error, dynamic time warping, Frechet distance, curvature.
- Space: Voronoi regions, controlled area, time to arrival, field control, space gained or lost.
- Expected performance: observed minus expected (O-E), CPOE, xYAC, EPA.
- ML and evaluation: linear and logistic regression, standardization, correlation, kNN, k-means, MAE, RMSE, accuracy, precision, recall, F1, Brier score.
- Counterfactuals and ghost trajectories.
- Metric design recipe: Player metric = observed performance minus expected performance. Steps: construct, operationalize, baseline, measure actual, compare, connect to outcome, validate (reliability, contextual controls, stability).

## Working style
Direct, objective feedback, no flattery. Light edits over rewrites. Keep Logan's own voice in any prose he will submit. No em dashes anywhere in prose. Do not over-explain corrections. Do not invent data, results or citations, and say plainly when something is unverified. Prefer reproducible code over one-off cells, and put reusable logic in shared/. Commit with clear messages and do not commit data.
