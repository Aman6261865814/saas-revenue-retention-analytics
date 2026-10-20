# Excel analyst workbook

Open analyst_workbook.xlsx. Overview has a validated category selector, XLOOKUP description, INDEX-MATCH fallback and a weighted KPI. Calculations uses SUMIF/SUMIFS over the Sources table; rates are ratios of sums, never averages of daily rates. Source values are synthetic aggregates; the workbook is a checked snapshot.

## Power Query refresh
Data > Get Data > From Text/CSV > source_metrics.csv > Transform Data. Set period as Date, category as Text, numerator/denominator as Decimal/Whole number as appropriate. Load to a separate table first and reconcile row counts and totals before replacing the existing source range. The Power BI fnLoadCSV.pq pattern can be reused in Excel. Refreshing a longer source requires extending formula ranges and the table; the provided snapshot has fixed bounds.

## Native PivotTable exercise
The supplied workbook contains formula summaries, not a native PivotTable. The export library's native pivot support could not be validated, so it is not presented as completed functionality.
1. Select the SourceMetrics table > Insert > PivotTable > New Worksheet.
2. Rows: category. Columns: period. Values: Sum of numerator and Sum of denominator.
3. Insert slicer for category. For SaaS, choose ONE period for a revenue snapshot.
4. Use a ratio of summed numerator to summed denominator beside the pivot, or a Data Model measure; do not average rates.
5. Refresh after source changes and reconcile the grand totals to Calculations.

Formulas and exports were checked using the workbook authoring engine. Native Excel execution/refresh has not been independently tested here.
