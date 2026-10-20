-- Run once in a new empty database. Never run against production without review.
CREATE TABLE cohort_retention (
    signup_month BIGINT NULL,
    age_month BIGINT NULL,
    active BIGINT NULL,
    cohort_size BIGINT NULL,
    retention DOUBLE NULL
);

CREATE TABLE dim_account (
    account_id BIGINT NOT NULL,
    region VARCHAR(255) NULL,
    segment VARCHAR(255) NULL,
    PRIMARY KEY (account_id)
);

CREATE TABLE fact_subscription (
    account_id BIGINT NOT NULL,
    month DATE NOT NULL,
    previous_mrr DECIMAL(19,4) NULL,
    mrr DECIMAL(19,4) NULL,
    movement VARCHAR(255) NULL,
    delta DOUBLE NULL,
    new_mrr DECIMAL(19,4) NULL,
    reactivation_mrr DECIMAL(19,4) NULL,
    expansion_mrr DECIMAL(19,4) NULL,
    contraction_mrr DECIMAL(19,4) NULL,
    churn_mrr DECIMAL(19,4) NULL,
    active BIGINT NULL,
    starting_active BIGINT NULL,
    churned BIGINT NULL,
    retained_mrr DECIMAL(19,4) NULL,
    age_month BIGINT NULL,
    PRIMARY KEY (account_id, month)
);

CREATE TABLE monthly_metrics (
    month DATE NULL,
    start_mrr DECIMAL(19,4) NULL,
    end_mrr DECIMAL(19,4) NULL,
    new_mrr DECIMAL(19,4) NULL,
    reactivation_mrr DECIMAL(19,4) NULL,
    expansion_mrr DECIMAL(19,4) NULL,
    contraction_mrr DECIMAL(19,4) NULL,
    churn_mrr DECIMAL(19,4) NULL,
    retained_mrr DECIMAL(19,4) NULL,
    active_accounts BIGINT NULL,
    starting_accounts BIGINT NULL,
    churned_accounts BIGINT NULL,
    nrr DOUBLE NULL,
    logo_churn_rate DOUBLE NULL,
    bridge_residual DOUBLE NULL
);