"""Deterministic metric verification for the synthetic FinOps scenario."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Iterable

ZERO = Decimal("0")
CENT = Decimal("0.01")
ONE_DECIMAL = Decimal("0.1")


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def _decimal(value: str) -> Decimal:
    return Decimal(value or "0")


def _sum(rows: Iterable[dict[str, str]], field: str) -> Decimal:
    return sum((_decimal(row[field]) for row in rows), ZERO)


def _group_sum(
    rows: Iterable[dict[str, str]], key: str, value: str
) -> dict[str, Decimal]:
    totals: dict[str, Decimal] = defaultdict(lambda: ZERO)
    for row in rows:
        totals[row[key]] += _decimal(row[value])
    return dict(sorted(totals.items(), key=lambda item: item[1], reverse=True))


def _parse_date(value: str) -> datetime:
    for pattern in ("%m/%d/%Y", "%m/%d/%y"):
        try:
            return datetime.strptime(value, pattern)
        except ValueError:
            continue
    raise ValueError(f"Unsupported date format: {value}")


def _money(value: Decimal) -> str:
    return f"{value.quantize(CENT):,.2f}"


def _pct(value: Decimal) -> str:
    return f"{value.quantize(ONE_DECIMAL)}"


def build_summary(data_dir: Path) -> dict[str, object]:
    budget_rows = _rows(data_dir / "finops_budget_tracking.csv")
    cloud_rows = _rows(data_dir / "finops_cloud_costs.csv")
    billing_rows = _rows(data_dir / "finops_billing_daily.csv")
    usage_rows = _rows(data_dir / "finops_usage_kpis_daily.csv")

    budget_total = _sum(budget_rows, "Monthly Budget")
    budget_actual = _sum(budget_rows, "Actual Cost")
    budget_variance = budget_total - budget_actual
    below_budget_pct = (budget_variance / budget_total) * Decimal("100")

    cloud_actual = _sum(cloud_rows, "Cost")
    potential_savings = _sum(cloud_rows, "Potential Savings")
    opportunity_pct = (potential_savings / cloud_actual) * Decimal("100")

    providers = _group_sum(cloud_rows, "Cloud Provider", "Cost")
    opportunity_status = _group_sum(
        cloud_rows, "Optimization Status", "Potential Savings"
    )
    opportunity_department = _group_sum(
        cloud_rows, "Department", "Potential Savings"
    )
    opportunity_service = _group_sum(cloud_rows, "Service", "Potential Savings")
    environments = _group_sum(cloud_rows, "Environment", "Cost")

    departments = sorted({row["Department"] for row in budget_rows})
    under_budget_rows = [
        row
        for row in budget_rows
        if _decimal(row["Actual Cost"]) <= _decimal(row["Monthly Budget"])
    ]

    billing_dates = sorted({_parse_date(row["date"]) for row in billing_rows})
    usage_dates = sorted({_parse_date(row["date"]) for row in usage_rows})
    gpu_rows = [
        row
        for row in billing_rows
        if "gpu" in row["resource_type"].lower()
    ]

    operational_spend = _sum(billing_rows, "cost_unblended_usd")
    gpu_spend = _sum(gpu_rows, "cost_unblended_usd")
    model_inferences = sum(int(row["model_inferences"]) for row in usage_rows)
    requests = sum(int(row["requests"]) for row in usage_rows)

    provider_pct = {
        provider: (amount / cloud_actual) * Decimal("100")
        for provider, amount in providers.items()
    }

    return {
        "executive_baseline": {
            "budget_rows": len(budget_rows),
            "departments": len(departments),
            "budget_total": budget_total,
            "actual_from_budget": budget_actual,
            "actual_from_cloud_costs": cloud_actual,
            "budget_variance": budget_variance,
            "below_budget_pct": below_budget_pct,
            "under_budget_rows": len(under_budget_rows),
            "potential_savings": potential_savings,
            "opportunity_pct": opportunity_pct,
            "cost_by_provider": providers,
            "provider_pct": provider_pct,
            "cost_by_environment": environments,
            "opportunity_by_status": opportunity_status,
            "opportunity_by_department": opportunity_department,
            "opportunity_by_service": opportunity_service,
        },
        "operational_extension": {
            "billing_rows": len(billing_rows),
            "usage_rows": len(usage_rows),
            "billing_days": len(billing_dates),
            "usage_days": len(usage_dates),
            "billing_first": billing_dates[0].date().isoformat(),
            "billing_last": billing_dates[-1].date().isoformat(),
            "usage_first": usage_dates[0].date().isoformat(),
            "usage_last": usage_dates[-1].date().isoformat(),
            "operational_spend": operational_spend,
            "gpu_rows": len(gpu_rows),
            "gpu_spend": gpu_spend,
            "model_inferences": model_inferences,
            "requests": requests,
        },
    }


def verify(summary: dict[str, object]) -> None:
    baseline = summary["executive_baseline"]
    operations = summary["operational_extension"]

    assert isinstance(baseline, dict)
    assert isinstance(operations, dict)

    assert baseline["budget_rows"] == 192
    assert baseline["departments"] == 8
    assert baseline["under_budget_rows"] == 192

    actual_budget = baseline["actual_from_budget"]
    actual_cloud = baseline["actual_from_cloud_costs"]
    assert isinstance(actual_budget, Decimal)
    assert isinstance(actual_cloud, Decimal)
    assert abs(actual_budget - actual_cloud) <= CENT

    potential = baseline["potential_savings"]
    statuses = baseline["opportunity_by_status"]
    assert isinstance(potential, Decimal)
    assert isinstance(statuses, dict)
    status_total = sum(statuses.values(), ZERO)
    assert abs(potential - status_total) <= CENT

    assert operations["billing_rows"] == 8548
    assert operations["usage_rows"] == 450
    assert operations["billing_days"] == 90
    assert operations["usage_days"] == 90
    assert operations["billing_first"] == "2025-11-03"
    assert operations["billing_last"] == "2026-01-31"
    assert operations["usage_first"] == "2025-11-03"
    assert operations["usage_last"] == "2026-01-31"


def _serializable(value: object) -> object:
    if isinstance(value, Decimal):
        return str(value.quantize(CENT))
    if isinstance(value, dict):
        return {key: _serializable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_serializable(item) for item in value]
    return value


def render(summary: dict[str, object]) -> str:
    baseline = summary["executive_baseline"]
    operations = summary["operational_extension"]

    assert isinstance(baseline, dict)
    assert isinstance(operations, dict)

    providers = baseline["cost_by_provider"]
    assert isinstance(providers, dict)

    return "\n".join(
        [
            "AI Infrastructure Intelligence — verified synthetic scenario",
            f"Budget baseline:              $ {_money(baseline['budget_total'])}",
            f"Actual spend:                 $ {_money(baseline['actual_from_cloud_costs'])}",
            f"Budget-to-actual variance:    $ {_money(baseline['budget_variance'])}",
            f"Below modeled budget:           {_pct(baseline['below_budget_pct'])}%",
            f"Additional opportunity:       $ {_money(baseline['potential_savings'])}",
            f"Opportunity / actual spend:     {_pct(baseline['opportunity_pct'])}%",
            f"AWS spend:                    $ {_money(providers['AWS'])}",
            f"GCP spend:                    $ {_money(providers['GCP'])}",
            f"90-day operational spend:     $ {_money(operations['operational_spend'])}",
            f"90-day GPU spend:             $ {_money(operations['gpu_spend'])}",
            f"90-day model inferences:        {operations['model_inferences']:,}",
            f"90-day requests:                {operations['requests']:,}",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    summary = build_summary(args.data_dir)

    if args.verify:
        verify(summary)

    if args.json:
        print(json.dumps(_serializable(summary), indent=2, sort_keys=True))
    else:
        print(render(summary))
        if args.verify:
            print("Verification: PASS")


if __name__ == "__main__":
    main()
