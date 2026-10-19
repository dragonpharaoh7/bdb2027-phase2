"""Download and unzip the competition data into data/raw.

Needs Kaggle credentials (KAGGLE_USERNAME and KAGGLE_KEY env vars, or
~/.kaggle/kaggle.json) and the competition rules accepted on kaggle.com.

    python -m shared.download
"""
import subprocess
import sys
import zipfile

from shared.config import COMPETITION, RAW


def main() -> None:
    zip_path = RAW / f"{COMPETITION}.zip"
    if not any(p for p in RAW.rglob("*") if p.suffix in {".csv", ".parquet"}):
        cmd = ["kaggle", "competitions", "download", "-c", COMPETITION, "-p", str(RAW)]
        print(" ".join(cmd))
        result = subprocess.run(cmd)
        if result.returncode != 0:
            sys.exit("Download failed. Check Kaggle credentials and that the rules are accepted.")
    else:
        print("Data files already present in data/raw, skipping download.")
    if zip_path.exists():
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(RAW)
        zip_path.unlink()
    files = sorted(p.relative_to(RAW) for p in RAW.rglob("*") if p.is_file() and p.name != ".gitkeep")
    print(f"{len(files)} files in data/raw")
    for f in files:
        print("  ", f)


if __name__ == "__main__":
    main()
