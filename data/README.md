# Data

## Public source

Download the **Telecom Customer Churn** dataset from the [Maven Analytics Data Playground](https://mavenanalytics.io/data-playground/telecom-customer-churn). Maven describes it as a public-domain sample sourced from IBM Cognos Analytics.

The project uses:

| Local filename | Description |
|---|---|
| `data/raw/telecom_customer_churn.csv` | One row per customer; demographics, account, services, charges, status, and churn reason |
| `data/raw/telecom_zipcode_population.csv` | Estimated population by California ZIP code |

The raw files are intentionally excluded from version control. This keeps the repository focused on reproducible code and directs users to the authoritative public source.

## Expected shape

- Customer table: 7,043 rows and 38 columns
- Unique customer IDs: 7,043
- Customer status values: `Stayed`, `Churned`, and `Joined`

## Generated files

Running `python scripts/preprocess.py` creates:

- `data/processed/telecom_customers_clean.csv`
- `outputs/tables/data_quality_summary.csv`
- `outputs/tables/kpi_summary.csv`
