-- 01_data_quality.sql
-- Run after loading data/processed/telecom_customers_clean.csv as telecom_customers.

SELECT
    COUNT(*) AS row_count,
    COUNT(DISTINCT customer_id) AS unique_customer_ids,
    SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) AS missing_customer_ids,
    SUM(invalid_monthly_charge_flag) AS invalid_monthly_charge_records,
    SUM(CASE WHEN population IS NULL THEN 1 ELSE 0 END) AS missing_population_records
FROM telecom_customers;

SELECT
    customer_status,
    COUNT(*) AS customers
FROM telecom_customers
GROUP BY customer_status
ORDER BY customers DESC;

SELECT
    invalid_monthly_charge_flag,
    customer_status,
    COUNT(*) AS customers,
    ROUND(AVG(monthly_charge_raw), 2) AS avg_monthly_charge_raw,
    ROUND(AVG(total_revenue), 2) AS avg_total_revenue
FROM telecom_customers
GROUP BY invalid_monthly_charge_flag, customer_status
ORDER BY invalid_monthly_charge_flag DESC, customers DESC;
