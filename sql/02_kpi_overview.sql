-- 02_kpi_overview.sql

WITH customer_kpis AS (
    SELECT
        COUNT(*) AS total_customers,
        SUM(churn_flag) AS churned_customers,
        AVG(churn_flag * 1.0) AS churn_rate,
        SUM(CASE WHEN churn_flag = 1 THEN monthly_charge_raw ELSE 0 END) AS monthly_revenue_exposure_raw,
        SUM(CASE WHEN churn_flag = 1 THEN total_revenue ELSE 0 END) AS historical_revenue_churned,
        AVG(CASE WHEN churn_flag = 1 THEN monthly_charge_valid END) AS avg_churned_charge_valid,
        AVG(CASE WHEN churn_flag = 1 THEN tenure_in_months END) AS avg_churned_tenure
    FROM telecom_customers
)
SELECT
    total_customers,
    churned_customers,
    ROUND(churn_rate * 100, 2) AS churn_rate_pct,
    ROUND(monthly_revenue_exposure_raw, 2) AS monthly_revenue_exposure_raw,
    ROUND(historical_revenue_churned, 2) AS historical_revenue_churned,
    ROUND(avg_churned_charge_valid, 2) AS avg_churned_charge_valid,
    ROUND(avg_churned_tenure, 2) AS avg_churned_tenure_months
FROM customer_kpis;

WITH status_summary AS (
    SELECT
        customer_status,
        COUNT(*) AS customers,
        SUM(monthly_charge_raw) AS monthly_charge_total,
        SUM(total_revenue) AS historical_revenue
    FROM telecom_customers
    GROUP BY customer_status
)
SELECT
    customer_status,
    customers,
    ROUND(customers * 100.0 / SUM(customers) OVER (), 2) AS customer_share_pct,
    ROUND(monthly_charge_total, 2) AS monthly_charge_total,
    ROUND(historical_revenue, 2) AS historical_revenue
FROM status_summary
ORDER BY customers DESC;
