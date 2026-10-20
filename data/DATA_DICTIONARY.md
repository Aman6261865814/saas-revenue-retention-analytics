# Data dictionary and metric contracts

All source data is synthetic, generated locally; no real organization or customer is represented.

## Grain and key
fact_subscription: one account_id + month, including zero balances before signup and after churn. dim_account: one row per account. Month is the start of the calendar month representing that month's normalized MRR snapshot.

## Core fields
previous_mrr: previous snapshot value, USD/month. mrr: current normalized monthly value. delta: mrr minus previous_mrr. new_mrr/reactivation_mrr/expansion_mrr: positive movement amounts. contraction_mrr/churn_mrr: negative movement amounts. retained_mrr: current MRR for accounts with previous_mrr > 0. active/starting_active/churned: binary indicators. age_month: month index minus signup index; negative values are pre-signup.

## Contracts
Opening MRR + new + reactivation + expansion + contraction + churn = closing MRR. NRR = retained_mrr / opening MRR. Month one has an undefined NRR, not zero. Cohort denominator is original cohort membership; reactivation is allowed. There is no FX, usage revenue, tax, discount or accrual accounting.

Additional table/column types, nulls and uniqueness are in reports/data_profile.csv.
