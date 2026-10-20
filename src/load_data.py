"""Load cleaned Olist CSVs from ./data into a local DuckDB database.

Download the files from your S3 Processed/ prefix into data/ first. Each file
must end in _cleaned.csv. This script does not access AWS or need credentials.
"""
from pathlib import Path
import re

import duckdb

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DB_PATH = ROOT / "olist.duckdb"


def table_name(filename):
    name = filename.removesuffix("_cleaned.csv")
    name = re.sub(r"[^a-zA-Z0-9_]", "_", name)
    return name.removeprefix("olist_")


def main():
    if not DATA_DIR.exists():
        raise SystemExit(f"Create {DATA_DIR} and download the cleaned CSVs from S3 Processed/ first.")
    files = sorted(DATA_DIR.glob("*_cleaned.csv"))
    if not files:
        raise SystemExit(f"No *_cleaned.csv files found in {DATA_DIR}.")

    con = duckdb.connect(str(DB_PATH))
    try:
        for path in files:
            table = table_name(path.name)
            # Escape single quotes in paths before passing them to DuckDB SQL.
            csv_path = str(path).replace("'", "''")
            con.execute(f'CREATE OR REPLACE TABLE "{table}" AS SELECT * FROM read_csv_auto(\'{csv_path}\', header=true)')
            count = con.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
            print(f"{table}: {count:,} rows")
    finally:
        con.close()
    print(f"DuckDB database created at {DB_PATH}")


if __name__ == "__main__":
    main()
