# Tableau dashboard

## Live version

[Telecom Customer Churn & Retention Analysis — Tableau Public](https://public.tableau.com/app/profile/jiangnan.wan/viz/shared/ZWMXJ95HW)

![Dashboard preview](dashboard_preview.jpg)

## Dashboard purpose

The dashboard gives a retention team a one-page view of churn scale, revenue exposure, high-risk account patterns, recorded churn reasons, and geographic variation.

## KPI cards

| KPI | Tableau definition | Displayed result |
|---|---|---:|
| Total Customers | Distinct customer count | 7,043 |
| Overall Churn Rate | Average of `Churn Flag` | 26.54% |
| MRR Lost | Sum of source monthly charge for churned customers | $137.09K |
| Average Tenure of Churned | Average tenure among churned customers | 17.98 months |

`MRR Lost` is retained as the original dashboard label for continuity. In the project documentation it is described more precisely as **monthly revenue exposure**, because the snapshot does not prove that the full amount becomes realized future loss.

## Main views

| View | Analytical role |
|---|---|
| Churn Rate by Contract Type | Compares the strongest account-level churn divide |
| Tenure vs Monthly Charge | Locates short-tenure and high-charge customers |
| Top Reasons for Customer Churn | Prioritizes competitor, support, price, and service issues |
| Churn Rate by ZIP Code | Shows geographic variation across California |
| Age Group Analysis | Compares customer-profile risk |
| Contract × Internet Type Heatmap | Identifies the month-to-month fiber-optic hotspot |

## Core calculated fields

```tableau
// Churn Flag
IF [Customer Status] = "Churned" THEN 1 ELSE 0 END

// Churn Rate
AVG([Churn Flag])

// Monthly Revenue Exposure / original workbook name: MRR Lost
IF [Customer Status] = "Churned" THEN [Monthly Charge] ELSE 0 END

// Churned Tenure
IF [Customer Status] = "Churned" THEN [Tenure in Months] END
```

## Interaction design

The workbook contains dashboard filter actions that allow selections in contract, reason, scatter, and geographic views to update the other components. This supports a workflow of:

1. Start with the KPI scale.
2. Select a high-risk segment.
3. Inspect its tenure-charge distribution and geography.
4. Review churn-reason composition.
5. Translate the segment into a targeted retention test.

## Files

- `telecom_churn_dashboard.twbx`: packaged workbook with embedded public sample data
- `dashboard_preview.jpg`: verified preview captured from the published Tableau Public view
