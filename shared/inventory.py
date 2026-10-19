"""Profile every raw CSV: rows, columns, dtypes, null rates, distinct counts, sample rows.
Writes data/processed/inventory.md so the schema is documented without hand-copying.

    python -m shared.inventory
"""
import pandas as pd

from shared.config import PROCESSED, RAW

CHUNK = 500_000
MAX_DISTINCT_TRACKED = 50_000


def profile(path) -> str:
    rows = 0
    nulls = None
    distinct = {}
    head = None
    dtypes = None
    for chunk in pd.read_csv(path, chunksize=CHUNK, low_memory=False):
        if head is None:
            head = chunk.head(3)
            dtypes = chunk.dtypes
            nulls = pd.Series(0, index=chunk.columns, dtype="int64")
            distinct = {c: set() for c in chunk.columns}
        rows += len(chunk)
        nulls += chunk.isna().sum()
        for c in chunk.columns:
            s = distinct[c]
            if s is not None:
                s.update(chunk[c].dropna().unique())
                if len(s) > MAX_DISTINCT_TRACKED:
                    distinct[c] = None
    lines = [f"## {path.relative_to(RAW)}", "", f"Rows: {rows:,}", "",
             "| column | dtype | null % | distinct |", "| --- | --- | --- | --- |"]
    for c in dtypes.index:
        d = distinct[c]
        dtxt = f">{MAX_DISTINCT_TRACKED:,}" if d is None else f"{len(d):,}"
        lines.append(f"| {c} | {dtypes[c]} | {100 * nulls[c] / max(rows, 1):.1f} | {dtxt} |")
    lines += ["", "Sample rows:", "", "```", head.to_string(index=False), "```", ""]
    return "\n".join(lines)


def main() -> None:
    files = sorted(RAW.rglob("*.csv"))
    if not files:
        raise SystemExit("No CSVs in data/raw. Run python -m shared.download first.")
    out = ["# Raw data inventory", ""]
    for f in files:
        print("profiling", f.relative_to(RAW))
        out.append(profile(f))
    dest = PROCESSED / "inventory.md"
    dest.write_text("\n".join(out))
    print("wrote", dest)


if __name__ == "__main__":
    main()
