"""Download and unzip the competition data into data/raw.

Needs Kaggle auth and the competition rules accepted on kaggle.com. Log in
once with OAuth:

    python -m kaggle auth login

That caches credentials in ~/.kaggle/credentials.json and refreshes them on its
own. As a fallback, set KAGGLE_API_TOKEN in .env at the repo root. kaggle CLI
2.2+ dropped the older KAGGLE_USERNAME / KAGGLE_KEY pair.

    python -m shared.download
"""
import subprocess
import sys
import zipfile

from shared.config import COMPETITION, RAW


def main() -> None:
    zip_path = RAW / f"{COMPETITION}.zip"
    if not any(p for p in RAW.rglob("*") if p.suffix in {".csv", ".parquet"}):
        # Use the running interpreter so this works without activating the venv.
        cmd = [sys.executable, "-m", "kaggle", "competitions", "download", "-c", COMPETITION, "-p", str(RAW)]
        print(" ".join(cmd))
        result = subprocess.run(cmd)
        if result.returncode != 0:
            sys.exit(
                "Download failed. Log in with 'python -m kaggle auth login' (or set "
                "KAGGLE_API_TOKEN in .env), and accept the competition rules at "
                f"kaggle.com/competitions/{COMPETITION}."
            )
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
