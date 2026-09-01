-- 04_retention_priority.sql
-- This is a transparent descriptive score, not a predictive probability.

WITH priority_summary AS (
    SELECT
        risk_priority,
        COUNT(*) AS customers,
        SUM(churn_flag) AS churned_customers,
        AVG(churn_flag * 1.0) AS observed_churn_rate,
        SUM(CASE WHEN churn_flag = 1 THEN monthly_charge_raw ELSE 0 END) AS monthly_revenue_exposure_raw
    FROM telecom_customers
    GROUP BY risk_priority
)
SELECT
    risk_priority,
    customers,
    churned_customers,
    ROUND(observed_churn_rate * 100, 2) AS observed_churn_rate_pct,
    ROUND(monthly_revenue_exposure_raw, 2) AS monthly_revenue_exposure_raw
FROM priority_summary
ORDER BY
    CASE risk_priority
        WHEN 'High' THEN 1
        WHEN 'Medium' THEN 2
        ELSE 3
    END;

SELECT
    customer_id,
    tenure_in_months,
    contract,
    internet_type_clean,
    monthly_charge_valid,
    total_revenue,
    descriptive_risk_score,
    risk_priority
FROM telecom_customers
WHERE customer_status IN ('Stayed', 'Joined')
  AND risk_priority = 'High'
ORDER BY monthly_charge_valid DESC, tenure_in_months ASC;
