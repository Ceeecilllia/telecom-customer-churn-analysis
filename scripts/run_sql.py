"""Execute every project SQL file against the cleaned customer table."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "telecom_customers_clean.csv"
SQL_DIR = PROJECT_ROOT / "sql"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "tables" / "sql_results"


def split_statements(sql: str) -> list[str]:
    """Split the project's simple read-only SQL files into statements."""
    return [statement.strip() for statement in sql.split(";") if statement.strip()]


def main() -> None:
    if not DATA_PATH.exists():
        raise FileNotFoundError("Run python scripts/preprocess.py before this script.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    customers = pd.read_csv(DATA_PATH)
    with sqlite3.connect(":memory:") as connection:
        customers.to_sql("telecom_customers", connection, index=False, if_exists="replace")
        for sql_path in sorted(SQL_DIR.glob("*.sql")):
            for index, statement in enumerate(split_statements(sql_path.read_text()), start=1):
                result = pd.read_sql_query(statement, connection)
                output_name = f"{sql_path.stem}_{index:02d}.csv"
                result.to_csv(OUTPUT_DIR / output_name, index=False)
                print(f"{sql_path.name} query {index}: {len(result):,} rows")


if __name__ == "__main__":
    main()
