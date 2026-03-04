# Data Quality Report (SaaS Churn Copilot)

- Input file: `data/accounts_synthetic.csv`
- Rows: 800
- Overall status: **PASS**

## Schema checks
- Missing required columns: None
- Duplicate account_id: 0

## Null checks
- account_id: 0 null(s) (0.00%)
- plan: 0 null(s) (0.00%)
- usage_90d: 0 null(s) (0.00%)
- usage_30d: 0 null(s) (0.00%)
- usage_delta_pct: 0 null(s) (0.00%)
- critical_tickets_30d: 0 null(s) (0.00%)
- nps: 0 null(s) (0.00%)
- on_time_payment_ratio: 0 null(s) (0.00%)
- late_payments_6m: 0 null(s) (0.00%)
- arr_usd: 0 null(s) (0.00%)

## Category checks
- plan: OK

## Range checks
- All numeric ranges look valid