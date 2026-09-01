-- 03_segment_analysis.sql
-- Reuse the same segment pattern for contract, internet type, payment, and services.

WITH contract_summary AS (
    SELECT
        contract,
        COUNT(*) AS customers,
        SUM(churn_flag) AS churned_customers,
        AVG(churn_flag * 1.0) AS churn_rate,
        AVG(monthly_charge_valid) AS avg_monthly_charge_valid,
        SUM(CASE WHEN churn_flag = 1 THEN monthly_charge_raw ELSE 0 END) AS monthly_revenue_exposure_raw
    FROM telecom_customers
    GROUP BY contract
)
SELECT
    contract,
    customers,
    churned_customers,
    ROUND(churn_rate * 100, 2) AS churn_rate_pct,
    ROUND(avg_monthly_charge_valid, 2) AS avg_monthly_charge_valid,
    ROUND(monthly_revenue_exposure_raw, 2) AS monthly_revenue_exposure_raw
FROM contract_summary
ORDER BY churn_rate DESC;

WITH contract_internet_summary AS (
    SELECT
        contract,
        internet_type_clean,
        COUNT(*) AS customers,
        SUM(churn_flag) AS churned_customers,
        AVG(churn_flag * 1.0) AS churn_rate
    FROM telecom_customers
    GROUP BY contract, internet_type_clean
)
SELECT
    contract,
    internet_type_clean,
    customers,
    churned_customers,
    ROUND(churn_rate * 100, 2) AS churn_rate_pct
FROM contract_internet_summary
ORDER BY churn_rate DESC, customers DESC;

WITH payment_summary AS (
    SELECT
        payment_method,
        COUNT(*) AS customers,
        SUM(churn_flag) AS churned_customers,
        AVG(churn_flag * 1.0) AS churn_rate,
        AVG(monthly_charge_valid) AS avg_monthly_charge_valid
    FROM telecom_customers
    GROUP BY payment_method
)
SELECT
    payment_method,
    customers,
    churned_customers,
    ROUND(churn_rate * 100, 2) AS churn_rate_pct,
    ROUND(avg_monthly_charge_valid, 2) AS avg_monthly_charge_valid
FROM payment_summary
ORDER BY churn_rate DESC;

WITH churn_reasons AS (
    SELECT
        churn_category,
        churn_reason,
        COUNT(*) AS churned_customers
    FROM telecom_customers
    WHERE churn_flag = 1
    GROUP BY churn_category, churn_reason
)
SELECT
    churn_category,
    churn_reason,
    churned_customers,
    ROUND(churned_customers * 100.0 / SUM(churned_customers) OVER (), 2) AS share_of_churn_pct
FROM churn_reasons
ORDER BY churned_customers DESC;
