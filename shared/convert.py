"""Convert every raw CSV to parquet (chunked, so large tracking files fit in memory).

    python -m shared.convert
"""
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from shared.config import PARQUET, RAW

CHUNK = 500_000


def csv_to_parquet(src, dst) -> int:
    writer = None
    rows = 0
    try:
        for chunk in pd.read_csv(src, chunksize=CHUNK, low_memory=False):
            table = pa.Table.from_pandas(chunk, preserve_index=False)
            if writer is None:
                writer = pq.ParquetWriter(dst, table.schema)
            else:
                table = table.cast(writer.schema, safe=False)
            writer.write_table(table)
            rows += len(chunk)
    finally:
        if writer is not None:
            writer.close()
    return rows


def main() -> None:
    for src in sorted(RAW.rglob("*.csv")):
        name = "__".join(src.relative_to(RAW).with_suffix("").parts)
        dst = PARQUET / f"{name}.parquet"
        if dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime:
            print(f"skip   {name}")
            continue
        rows = csv_to_parquet(src, dst)
        print(f"wrote  {name}  ({rows:,} rows)")


if __name__ == "__main__":
    main()
