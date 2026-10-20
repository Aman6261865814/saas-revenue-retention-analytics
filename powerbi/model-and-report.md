# Power BI implementation: SaaS Revenue & Retention Observatory

Status: import-ready CSV, Power Query, DAX, theme and RLS design supplied. No .pbix is included; Desktop/Service validation has not been performed.

1. Open Power BI Desktop, define `DataFolder` as an absolute path to data/processed.
2. Create fnLoadCSV from the supplied M function. Create `fact_subscription` using fact_query.pq. Import remaining needed dimensions using Get Data > Text/CSV. Set IDs to whole number and money to fixed decimal.
3. Create `dim_date = CALENDAR(MIN(fact_subscription[month]), MAX(fact_subscription[month]))`, mark Date as date table; connect dim_date[Date] 1:* to fact_subscription[month], single-direction.
4. Import dim_account, unique account_id; connect 1:* to fact_subscription. Region and segment slicers must come from dim_account.
5. Add each measure separately from measures.dax. Import theme.json. Currency USD, rate measures 0.0%, pp measures 0.00.
6. Import security.csv separately, replace sample UPNs, keep it disconnected. In Manage roles add supplied rls.dax filter. Unknown users receive no rows. Never use a permissive default region.
7. Test View as with one UPN per region, an unknown user, and a user assigned two regions. Compare regional totals with CSV/Python. Test again as a **Viewer** in Service; RLS does not restrict workspace Admins, Members or Contributors.
8. Publish only after local totals match reports/metrics.json. Set refresh credentials/gateway for local file sources or replace with governed database sources; a local path will not auto-refresh in Service by itself.

## Three-page report specification

| Page | Visuals | Interaction / acceptance |
|---|---|---|
| Executive overview | KPI cards; primary trend or comparison; concise decision annotation | Date and region slicers; labels show units and synthetic source |
| Drivers | MRR movement waterfall, segment matrix and cohort heatmap | Drill-through to business key; tooltips explain denominators |
| Data quality | Duplicate count, grain check, freshness and null coverage | Link to validation evidence and metric definitions |

## Semantic safeguards

Snapshot MRR is semi-additive: require a SINGLE month selection for MRR/NRR cards and disable Select all. Do not sum MRR across months. Latest MRR is intended for full-month selections only. Use month on chart axis. Disconnected monthly/cohort aggregates are analyst-only and must NOT be loaded into a region-secured published model; they lack account-level RLS. Build cohort visuals from the fact and dimensions.

## References

- https://learn.microsoft.com/en-us/power-bi/guidance/star-schema
- https://learn.microsoft.com/en-us/power-bi/enterprise/service-admin-rls
