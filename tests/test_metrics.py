from decimal import Decimal
from pathlib import Path
import unittest

from finops_intelligence.metrics import build_summary, verify


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


class MetricsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.summary = build_summary(DATA_DIR)

    def test_full_verification_contract(self) -> None:
        verify(self.summary)

    def test_financial_reconciliation(self) -> None:
        baseline = self.summary["executive_baseline"]
        self.assertEqual(
            baseline["actual_from_budget"].quantize(Decimal("0.01")),
            Decimal("3812936.30"),
        )
        self.assertEqual(
            baseline["actual_from_cloud_costs"].quantize(Decimal("0.01")),
            Decimal("3812936.30"),
        )
        self.assertEqual(
            baseline["budget_variance"].quantize(Decimal("0.01")),
            Decimal("5382832.42"),
        )

    def test_all_department_months_remain_under_budget(self) -> None:
        baseline = self.summary["executive_baseline"]
        self.assertEqual(baseline["budget_rows"], 192)
        self.assertEqual(baseline["under_budget_rows"], 192)
        self.assertEqual(baseline["departments"], 8)

    def test_optimization_backlog_reconciles(self) -> None:
        baseline = self.summary["executive_baseline"]
        self.assertEqual(
            baseline["potential_savings"].quantize(Decimal("0.01")),
            Decimal("207406.70"),
        )
        self.assertEqual(
            baseline["opportunity_by_status"]["Reserved Instance Candidate"].quantize(
                Decimal("0.01")
            ),
            Decimal("130453.01"),
        )

    def test_operational_window_is_separate_and_complete(self) -> None:
        operations = self.summary["operational_extension"]
        self.assertEqual(operations["billing_days"], 90)
        self.assertEqual(operations["usage_days"], 90)
        self.assertEqual(operations["billing_first"], "2025-11-03")
        self.assertEqual(operations["billing_last"], "2026-01-31")
        self.assertEqual(
            operations["gpu_spend"].quantize(Decimal("0.01")),
            Decimal("25829.78"),
        )
        self.assertEqual(operations["model_inferences"], 280915)


if __name__ == "__main__":
    unittest.main()
