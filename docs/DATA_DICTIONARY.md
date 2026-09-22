# Data Dictionary

The repository contains two independent synthetic evidence windows. They are deliberately kept separate so metrics from different periods are not accidentally combined.

## Executive baseline — January 2023 through December 2024

### `finops_budget_tracking.csv`

**Grain:** one row per department per month  
**Rows:** 192  
**Coverage:** 8 departments × 24 months

| Column | Meaning |
| --- | --- |
| `Date` | First day of the modeled month |
| `Department` | Cost-owning department |
| `Monthly Budget` | Synthetic monthly budget target |
| `Actual Cost` | Synthetic actual cloud cost allocated to the department |
| `Variance` | Actual cost minus budget in the source data |
| `Variance %` | Variance as a percentage of budget |

This file is the executive budget-control view.

### `finops_cloud_costs.csv`

**Grain:** modeled monthly cloud-cost allocation line  
**Rows:** 21,051  
**Providers:** AWS and GCP  
**Coverage:** January 2023 through December 2024

Key dimensions include provider, service, department, project, region, environment, cost center, and optimization status.

| Column | Meaning |
| --- | --- |
| `Cost` | Modeled allocated cloud spend |
| `Usage` | Modeled service usage quantity |
| `Optimization Status` | Scenario classification used to describe the optimization backlog |
| `Potential Savings` | Modeled opportunity amount associated with the row |

The sum of `Cost` reconciles to the sum of `Actual Cost` in the budget-tracking dataset.

## Operational AI infrastructure extension — November 3, 2025 through January 31, 2026

### `finops_billing_daily.csv`

**Grain:** daily resource billing record  
**Rows:** 8,548  
**Coverage:** 90 calendar days  
**Providers:** AWS and GCP

The file includes synthetic account/project identifiers, services, regions, resource identifiers, resource types, unblended cost, usage, and allocation tags.

GPU analysis uses only rows whose `resource_type` explicitly contains `gpu`.

### `finops_usage_kpis_daily.csv`

**Grain:** one row per team per day  
**Rows:** 450  
**Coverage:** 5 teams × 90 days

| Column | Meaning |
| --- | --- |
| `active_users` | Modeled daily active users |
| `requests` | Modeled application/API request volume |
| `jobs_run` | Modeled batch or platform job count |
| `gb_processed` | Modeled processed data volume |
| `model_inferences` | Modeled inference count |

This file provides the usage side of the AI infrastructure economics story.

## Important interpretation rule

The 2023–2024 baseline and 2025–2026 operational extension answer different questions and must not be aggregated into one continuous financial time series.
