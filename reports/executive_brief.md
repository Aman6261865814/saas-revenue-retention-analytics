# SaaS Revenue & Retention Observatory

SYNTHETIC PORTFOLIO CASE STUDY — not actual company results.

## Decision
Ending MRR is $528,130.30; latest-month NRR is 97.6%. Inspect churn and contraction by segment before funding acquisition.

## Evidence
43,200 account-month snapshots; 200 exact retry duplicates removed. All 18 revenue bridges reconcile to floating-point tolerance. NRR follows accounts paying at the start of each month; new and reactivated accounts are excluded.

## Limits and next action
MRR is normalized subscription value, not recognized revenue or cash collected. Retention includes reactivation, so cohort curves may rise. The final cohorts have shorter observation windows, not zero retention in future months. Segment comparisons are descriptive, not causal. Validate billing adjustments and constant-currency rules before a production rollout.
