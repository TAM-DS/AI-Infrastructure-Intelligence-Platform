# AI Infrastructure Intelligence Platform
### Evidence-led FinOps for multi-cloud AI infrastructure

> **Cloud optimization is not a contest to produce the largest savings number. It is a decision system: establish the baseline, reconcile spend, identify the next best action, and preserve the evidence behind the decision.**

This repository models that decision loop across AWS and Google Cloud using fully synthetic data. It combines executive budget tracking, detailed cloud cost allocation, daily resource billing, and AI/ML usage telemetry so infrastructure economics can be examined from both a finance and platform-engineering perspective.

## Executive decision summary

Every headline number below is reproducible from the committed datasets.

| Decision metric | Verified result | Evidence window |
| --- | ---: | --- |
| Modeled budget baseline | **$9,195,768.72** | Jan 2023 – Dec 2024 |
| Modeled actual cloud spend | **$3,812,936.30** | Jan 2023 – Dec 2024 |
| Budget-to-actual variance | **$5,382,832.42** | Jan 2023 – Dec 2024 |
| Spend below modeled budget | **58.5%** | Jan 2023 – Dec 2024 |
| Departments under monthly budget | **8 of 8, all 24 months** | Jan 2023 – Dec 2024 |
| Additional modeled optimization opportunity | **$207,406.70** | Jan 2023 – Dec 2024 |
| Opportunity as share of actual spend | **5.4%** | Jan 2023 – Dec 2024 |
| AWS / GCP actual spend mix | **59.3% / 40.7%** | Jan 2023 – Dec 2024 |

The `$5.38M` figure is intentionally described as **budget-to-actual variance**, not automatically as realized savings. The separate `$207.4K` figure represents modeled optimization opportunities still present in the detailed cost data.

### Optimization backlog

| Opportunity class | Modeled opportunity |
| --- | ---: |
| Reserved Instance candidates | **$130,453.01** |
| Potential waste | **$45,983.85** |
| Right-sizing opportunities | **$30,969.84** |
| **Total** | **$207,406.70** |

The largest service-level opportunities are concentrated in EC2, Compute Engine, RDS, BigQuery, EBS, and Cloud SQL.

## The second evidence window: AI infrastructure operations

The repository also contains a separate 90-day operational extension from **November 3, 2025 through January 31, 2026**. It is not blended into the 2023–2024 executive baseline.

| Operational metric | Verified result |
| --- | ---: |
| Daily billing rows | **8,548** |
| Modeled 90-day spend | **$94,410.59** |
| Modeled GPU spend | **$25,829.78** |
| GPU resource records | **915** |
| Daily usage KPI rows | **450** |
| Model inferences | **280,915** |
| Application requests | **15,831,113** |

This second window creates the bridge from traditional FinOps into **AI infrastructure unit economics**: cloud cost can be viewed alongside requests, jobs, processed data, and model inference volume.

## Decision contract

The repository follows four rules:

1. **A budget gap is not automatically called savings.** It is reported as variance unless the evidence proves realized savings.
2. **Candidate savings are not booked savings.** Potential optimization is kept separate from historical spend.
3. **Time windows do not silently mix.** The 2023–2024 executive baseline and 2025–2026 operational telemetry are analyzed independently.
4. **Headline claims must be reproducible.** The verification module recomputes the metrics from the committed source files and fails if reconciliation breaks.

That distinction is the difference between a dashboard that looks persuasive and an analytical system that can support a decision.

## Executive evidence gallery

Seven captures from the functioning **AI Infrastructure Economics Control Tower**. All source data is **synthetic**; the 2023–2024 finance baseline and November 2025–January 2026 operations are deliberately separate. Token counts, rates, routing percentages, retries, and growth below are **what-if inputs**, not observed token billing.

### 01 · AI Infrastructure Command Center

![Executive dashboard: 90-day cloud spend, GPU cost concentration, application requests, and synthetic inference volume](docs/images/tower-01-command-center.png)

The executive operating picture tracks **$94,410.59 in modeled 90-day cloud spending**, including **$25,829.78 GPU-tagged cost**, alongside **280,915 synthetic inferences**. A concentration signal alone does not prove waste.

### 02 · Token Economics: scenario model

![Interactive hypothetical token-cost view with input/output cost categories and scenario assumptions](docs/images/tower-02-token-economics.png)

An explicit planning model translates synthetic inference volume into **hypothetical** token economics. Token counts, prices, and retry costs are user-adjustable assumptions, **not measured charges**.

### 03 · Model Routing Sensitivity

![Token-cost sensitivity under alternate model routing assumptions](docs/images/tower-03-routing-sensitivity.png)

The lower-cost model-routing slider changes projected token expenditure; cost savings should be assessed against **model quality, latency, and safety evaluations**, not price alone.

### 04 · Cloud Optimization

![Historical finance baseline and modeled optimization opportunity dashboard](docs/images/tower-04-cloud-optimization.png)

The historical synthetic dataset separates **$9.20M modeled budget**, **$3.81M actual modeled allocation**, **$5.38M budget variance**, and **$207.4K potential optimization opportunity**. A budget gap is *not* booked savings.

### 05 · Budget Versus Synthetic Actual

![Monthly 2023–2024 budget and synthetic actual cloud spend comparison](docs/images/tower-05-budget-vs-actual.png)

Department-level budget and historical cloud costs reconcile over the 2023–2024 baseline; this historical chart is **not mixed** with the subsequent 90-day inference telemetry.

### 06 · Planning Assumptions

![Sidebar controls for assumed tokens per inference, routing mix, retries, price inputs, and growth](docs/images/tower-06-planning-assumptions.png)

Visible scenario controls make the model's assumptions challengeable by a client or executive. The token-cost plan must **not** be added to historical cloud billing because the datasets do not establish mutually exclusive charges.

### 07 · Executive Decision Controls

![Executive review queue with evidence classes, testable data-lineage controls, and accountable recommendations](docs/images/tower-07-decision-controls.png)

The review queue distinguishes **source observations, derived results, scenario assumptions, and human sign-off**. Recommendations are read-only; no cloud remediation or purchasing actions are performed.

> **Evidence contract:** This is a synthetic portfolio reference implementation, not a deployed client platform, token invoice, realized-savings claim, or live production security assessment. Reproduce verified metrics with the standard-library financial verifier and review what-if assumptions separately.

## Interactive AI Infrastructure Economics Control Tower

**Executive decision:** Can leadership distinguish evidenced cloud consumption, potential optimization, and *modeled* AI token economics before approving changes?

The **Streamlit + Plotly control tower** contains four interactive views:

| Executive workspace | What it demonstrates |
| --- | --- |
| **Command Center** | Synthetic 90-day daily costs, GPU cost concentration, inference volume, and review signals |
| **Token Economics** | Editable hypothetical input/output tokens, model pricing tiers, routing mix, retry overhead, and volume growth |
| **Cloud Optimization** | Separate 2023–24 budget reconciliation, actual allocation, provider costs, and optimization candidates |
| **Decision Controls** | Evidence lineage, limitations, human decision rights, and actionable follow-up questions |

### Run locally

Requires Python 3.11+. From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-tower.txt
PYTHONPATH=src python -m unittest discover -s tests -v
python -m streamlit run streamlit_app.py
```

Open the local URL printed by Streamlit (usually `http://localhost:8501`).

### Financial evidence boundaries

- **2023–24 baseline**: $9.196M modeled budget, $3.813M modeled actuals and $5.383M budget variance. **Variance is not savings.**
- **2025–26 operational window**: $94.41K modeled 90-day cloud spending, $25.83K GPU-tagged costs and 280,915 synthetic inferences. This is **not** the same time window as the budget baseline.
- **Token planning**: no input/output token counts, token bills, model prices, latency, eval results, or actual retry logs exist in the committed source. Rates and tokens per inference are clearly labeled **hypothetical assumptions**; the scenario must **not** be added to historical cloud spend, because cloud charges may already include overlapping costs.
- **Executive decision**: model outputs are for analysis and human review, not autonomously booked savings, purchasing decisions, or production security assessments.

The application is **local, read-only, and synthetic-data-only**: no external cloud access or live client data.

## Implemented analytical flow

```mermaid
flowchart LR
    Budget["Department budget targets<br/>2023–2024"]
    Cost["AWS + GCP allocated cost<br/>2023–2024"]
    Billing["Daily resource billing<br/>2025–2026"]
    Usage["Daily AI/ML usage KPIs<br/>2025–2026"]

    Normalize["Normalize & validate"]
    Reconcile["Budget / actual reconciliation"]
    Opportunity["Optimization opportunity model"]
    Economics["AI infrastructure unit economics"]
    Evidence["Decision evidence"]

    Budget --> Normalize
    Cost --> Normalize
    Billing --> Normalize
    Usage --> Normalize

    Normalize --> Reconcile
    Normalize --> Opportunity
    Normalize --> Economics

    Reconcile --> Evidence
    Opportunity --> Evidence
    Economics --> Evidence

    Evidence --> CFO["CFO / FinOps decisions"]
    Evidence --> Platform["Platform / MLOps decisions"]
```

## What the data says

For the 2023–2024 modeled baseline:

- AWS accounts for **$2.262M** of spend and GCP **$1.551M**.
- Production represents **$3.111M** of the **$3.813M** actual spend.
- The committed budget table and detailed cloud-cost table reconcile to the same **$3,812,936.30** actual total.
- Every department remains below its modeled monthly budget for all 24 periods.
- Data Science has the largest modeled optimization backlog at about **$32.6K**, followed by Engineering at about **$30.4K**.

For the 2025–2026 operational extension:

- GCP represents **$64.9K** of the 90-day modeled spend and AWS **$29.5K**.
- GPU-tagged resource spend totals **$25.8K**, split between modeled L4 and A10 resource types.
- MLOps generates the largest inference volume; Platform generates the largest request volume.

These are **observations from the synthetic scenario**, not claims about a live production estate.

## Repository structure

```text
.
├── data/
│   ├── finops_budget_tracking.csv
│   ├── finops_cloud_costs.csv
│   ├── finops_billing_daily.csv
│   └── finops_usage_kpis_daily.csv
├── docs/
│   ├── DATA_DICTIONARY.md
│   ├── METRIC_LINEAGE.md
│   └── images/
│       ├── dashboard-01.jpg
│       └── dashboard-02.jpg
├── src/
│   └── finops_intelligence/
│       ├── __init__.py
│       └── metrics.py
├── tests/
│   └── test_metrics.py
├── .github/workflows/ci.yml
└── README.md
```

## Reproduce the evidence

The analytical verifier uses only the Python standard library.

```bash
PYTHONPATH=src python -m finops_intelligence.metrics --data-dir data --verify
PYTHONPATH=src python -m unittest discover -s tests -v
```

The verifier checks, among other things:

- actual spend reconciles across the budget and detailed cost datasets;
- all 192 department-month observations are below their modeled budgets;
- the optimization backlog reconciles to its component opportunity classes;
- the operational billing and usage datasets cover the same 90-day window;
- GPU spend is calculated only from resource types explicitly tagged as GPU resources.

CI runs compilation, tests, deterministic metric verification, and a whitespace check on every push and pull request.

## Data provenance and limitations

All data in this repository is **fully synthetic**. It is modeled on realistic enterprise cloud billing and FinOps patterns, but it contains no real cloud account information, customer data, PII, or proprietary billing records.

The project contains two intentionally separate analytical periods:

- **Executive baseline:** January 2023 – December 2024.
- **Operational AI infrastructure extension:** November 3, 2025 – January 31, 2026.

See [DATA_DICTIONARY.md](docs/DATA_DICTIONARY.md) for dataset grain and [METRIC_LINEAGE.md](docs/METRIC_LINEAGE.md) for formulas and interpretation rules.

## Portfolio framing

This project is not intended to simulate an entire FinOps commercial platform. It demonstrates the architectural judgment behind one:

**cost telemetry → normalization → reconciliation → opportunity → evidence → business decision**

The most important design choice is not the dashboard. It is the boundary between **what the data proves**, **what the model estimates**, and **what the business chooses to do next**.

---

Built by Tracy Anne Griffin Manning  
[LinkedIn](https://www.linkedin.com/in/tracy-manning-systems-architect) · [Tableau Dashboard](https://tinyurl.com/mr3a9yce)
