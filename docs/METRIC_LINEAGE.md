# Metric Lineage

Every headline metric in the README is derived deterministically from committed synthetic data.

## 2023–2024 executive baseline

### Modeled budget baseline

```text
SUM(finops_budget_tracking.Monthly Budget)
= $9,195,768.72
```

### Modeled actual spend

```text
SUM(finops_budget_tracking.Actual Cost)
= $3,812,936.30
```

The detailed cost file independently reconciles to the same total:

```text
SUM(finops_cloud_costs.Cost)
= $3,812,936.30
```

### Budget-to-actual variance

```text
SUM(Monthly Budget) - SUM(Actual Cost)
= $5,382,832.42
```

### Spend below modeled budget

```text
Budget-to-actual variance / SUM(Monthly Budget)
= 58.5%
```

This is a **budget variance**, not automatically realized savings.

### Departments under monthly budget

For every row:

```text
Actual Cost <= Monthly Budget
```

The dataset contains 192 department-month observations: 8 departments × 24 months. All 192 satisfy the condition.

### Additional modeled optimization opportunity

```text
SUM(finops_cloud_costs.Potential Savings)
= $207,406.70
```

By opportunity class:

| Optimization status | Amount |
| --- | ---: |
| Reserved Instance Candidate | $130,453.01 |
| Potential Waste | $45,983.85 |
| Right-sizing Opportunity | $30,969.84 |
| Optimized | $0.00 |
| **Total** | **$207,406.70** |

### Opportunity as share of actual spend

```text
$207,406.70 / $3,812,936.30
= 5.4%
```

### Provider mix

```text
AWS = $2,261,522.60 = 59.3%
GCP = $1,551,413.70 = 40.7%
```

## 2025–2026 operational extension

### Modeled 90-day spend

```text
SUM(finops_billing_daily.cost_unblended_usd)
= $94,410.59
```

### Modeled GPU spend

Rows are included only when `resource_type` contains the literal token `gpu`.

```text
SUM(cost_unblended_usd WHERE resource_type CONTAINS "gpu")
= $25,829.78
```

### Model inference volume

```text
SUM(finops_usage_kpis_daily.model_inferences)
= 280,915
```

### Application request volume

```text
SUM(finops_usage_kpis_daily.requests)
= 15,831,113
```

## Reconciliation control

The verifier fails if the budget dataset's actual spend and the detailed cloud-cost dataset differ by more than one cent.

That control prevents an executive metric from silently drifting away from its underlying allocation data.
