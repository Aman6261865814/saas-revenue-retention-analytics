# SaaS Revenue Analytics — completed Power BI report

Verified: 13 October 2026.

Open `SaaS Revenue Analytics.pbix` in Power BI Desktop. The adjacent PBIP and Report/SemanticModel folders preserve the editable project source.

## Report pages
- Revenue overview: five June 2026 KPI cards, monthly MRR trend, segment comparison, region and segment filters.
- Cohort retention: signup-month rows and months-since-signup columns; percentages show active accounts divided by original cohort size. Future observations remain blank. Reactivation can increase retention.

## Verified results
- Latest MRR: USD 528,130.30.
- Active accounts: 1,928.
- Net revenue retention: 97.59%.
- Logo churn: 1.85%.
- MRR per active account: USD 273.93.
- Region test (APAC): MRR USD 133,699.70; active accounts 474.
- Segment test (Enterprise): MRR USD 313,102.05; active accounts 191.
- January 2025 cohort: 100.0% at signup, 99.4% at month 1, 74.2% at month 12.
- Both overview selectors restored to All before saving.

## Scope and usage
The report uses synthetic portfolio data, with 43,200 account-month records across 2,400 accounts and 18 months. The overview filters affect account-level metrics. The cohort page uses a global pre-aggregated cohort table, so overview region/segment selections do not filter it.

Snapshot cards use the latest available data month; they are not sums across the full history. Net revenue retention excludes new and reactivated accounts. MRR is recurring subscription value, not collected cash.

The saved import data can be viewed without refreshing. Refresh requires the configured local SQL Server database `localhost/SaaSRevenueAnalytics`. This report has not been published to Power BI Service.
