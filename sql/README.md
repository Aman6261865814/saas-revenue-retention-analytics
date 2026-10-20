# Database setup and verification

SQLite is already populated. Open data/analytics.sqlite in a SQLite client and run analysis.sqlite.sql, advanced_queries.sql and performance.sql.

For SQL Server 2019+ (SSMS) or MySQL 8.0+ (Workbench):
1. Create a new empty portfolio database. Run schema.sqlserver.sql or schema.mysql.sql.
2. Import each data/processed CSV into its identically named table. Preserve the header mapping and SQL NULL for blank numeric/date fields. Import dim_account before facts in the SaaS project.
3. Confirm row counts against reports/data_profile.csv and primary-key uniqueness. These scripts deliberately do not drop existing tables.
4. Run the matching analysis script and compare to reports/sql_result.csv. Float rate differences within 1e-9 are acceptable; counts must match exactly.
5. Create the matching stored procedure and call it with an inclusive start and exclusive end date. For SaaS, a multi-month range returns a sum of snapshots, not ending MRR; use a single month for ending MRR.
6. Inspect actual query plans on your own server. Use query_plan_evidence.json only as local SQLite evidence.

Target database scripts have not been executed on SQL Server or MySQL in this delivery. Authentication, permissions and server-specific import tools must be configured by the user. No credentials are embedded.
