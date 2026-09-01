"""Validate and prepare the Maven telecom churn dataset for analysis."""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_CUSTOMERS = PROJECT_ROOT / "data" / "raw" / "telecom_customer_churn.csv"
RAW_POPULATION = PROJECT_ROOT / "data" / "raw" / "telecom_zipcode_population.csv"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables"

EXPECTED_CUSTOMER_ROWS = 7_043
EXPECTED_CUSTOMER_COLUMNS = 38


def to_snake_case(value: str) -> str:
    """Convert a source column name to a stable SQL-friendly name."""
    value = re.sub(r"[^0-9A-Za-z]+", "_", value.strip())
    return value.strip("_").lower()


def load_source_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    if not RAW_CUSTOMERS.exists() or not RAW_POPULATION.exists():
        raise FileNotFoundError(
            "Missing raw CSV files. Follow data/README.md and place both files in data/raw/."
        )
    return pd.read_csv(RAW_CUSTOMERS), pd.read_csv(RAW_POPULATION)


def validate_source(customers: pd.DataFrame) -> None:
    if customers.shape != (EXPECTED_CUSTOMER_ROWS, EXPECTED_CUSTOMER_COLUMNS):
        raise ValueError(
            "Unexpected customer-table shape: "
            f"{customers.shape}; expected {(EXPECTED_CUSTOMER_ROWS, EXPECTED_CUSTOMER_COLUMNS)}."
        )
    if customers["Customer ID"].isna().any():
        raise ValueError("Customer ID contains missing values.")
    if customers["Customer ID"].duplicated().any():
        raise ValueError("Customer ID is not unique.")
    expected_statuses = {"Stayed", "Churned", "Joined"}
    actual_statuses = set(customers["Customer Status"].dropna().unique())
    if actual_statuses != expected_statuses:
        raise ValueError(f"Unexpected customer statuses: {sorted(actual_statuses)}")


def prepare_customer_table(
    customers: pd.DataFrame, population: pd.DataFrame
) -> pd.DataFrame:
    customers = customers.copy()
    population = population.copy()
    customers.columns = [to_snake_case(column) for column in customers.columns]
    population.columns = [to_snake_case(column) for column in population.columns]

    customers["zip_code"] = customers["zip_code"].astype("Int64")
    population["zip_code"] = population["zip_code"].astype("Int64")
    clean = customers.merge(population, on="zip_code", how="left", validate="many_to_one")

    clean = clean.rename(columns={"monthly_charge": "monthly_charge_raw"})
    clean["invalid_monthly_charge_flag"] = clean["monthly_charge_raw"].lt(0).astype("int8")
    clean["monthly_charge_valid"] = clean["monthly_charge_raw"].where(
        clean["monthly_charge_raw"].ge(0), np.nan
    )
    clean["churn_flag"] = clean["customer_status"].eq("Churned").astype("int8")
    clean["joined_flag"] = clean["customer_status"].eq("Joined").astype("int8")
    clean["short_tenure_flag"] = clean["tenure_in_months"].lt(12).astype("int8")
    clean["high_charge_flag"] = clean["monthly_charge_valid"].ge(70).astype("int8")
    clean["internet_type_clean"] = clean["internet_type"].fillna("No Internet Service")
    clean["offer_clean"] = clean["offer"].fillna("No Offer").replace("None", "No Offer")

    high_risk_conditions = (
        clean["contract"].eq("Month-to-Month").astype("int8")
        + clean["short_tenure_flag"]
        + clean["high_charge_flag"]
        + clean["internet_type_clean"].eq("Fiber Optic").astype("int8")
    )
    clean["descriptive_risk_score"] = high_risk_conditions
    clean["risk_priority"] = pd.cut(
        clean["descriptive_risk_score"],
        bins=[-1, 1, 2, 4],
        labels=["Low", "Medium", "High"],
    ).astype("string")
    return clean


def build_quality_summary(raw: pd.DataFrame, clean: pd.DataFrame) -> pd.DataFrame:
    checks = [
        ("source_rows", len(raw)),
        ("source_columns", raw.shape[1]),
        ("unique_customer_ids", raw["Customer ID"].nunique()),
        ("duplicate_customer_ids", int(raw["Customer ID"].duplicated().sum())),
        ("missing_customer_ids", int(raw["Customer ID"].isna().sum())),
        ("negative_monthly_charge_records", int(clean["invalid_monthly_charge_flag"].sum())),
        ("missing_population_after_join", int(clean["population"].isna().sum())),
    ]
    return pd.DataFrame(checks, columns=["check", "value"])


def build_kpi_summary(clean: pd.DataFrame) -> pd.DataFrame:
    churned = clean[clean["churn_flag"].eq(1)]
    metrics = [
        ("total_customers", len(clean)),
        ("churned_customers", int(churned.shape[0])),
        ("churn_rate_pct", round(clean["churn_flag"].mean() * 100, 2)),
        ("monthly_revenue_exposure_raw", round(churned["monthly_charge_raw"].sum(), 2)),
        ("historical_revenue_churned", round(churned["total_revenue"].sum(), 2)),
        ("avg_churned_monthly_charge_valid", round(churned["monthly_charge_valid"].mean(), 2)),
        ("avg_churned_tenure_months", round(churned["tenure_in_months"].mean(), 2)),
    ]
    return pd.DataFrame(metrics, columns=["metric", "value"])


def main() -> None:
    customers, population = load_source_data()
    validate_source(customers)
    clean = prepare_customer_table(customers, population)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    clean.to_csv(PROCESSED_DIR / "telecom_customers_clean.csv", index=False)
    build_quality_summary(customers, clean).to_csv(
        OUTPUT_TABLE_DIR / "data_quality_summary.csv", index=False
    )
    build_kpi_summary(clean).to_csv(OUTPUT_TABLE_DIR / "kpi_summary.csv", index=False)

    print(f"Prepared {len(clean):,} customer records with {clean.shape[1]} analysis fields.")
    print(f"Negative monthly-charge records flagged: {clean['invalid_monthly_charge_flag'].sum():,}")


if __name__ == "__main__":
    main()
