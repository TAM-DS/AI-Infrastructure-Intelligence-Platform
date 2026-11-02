"""Deterministic controls for standalone hypothetical token planning."""
from decimal import Decimal
import unittest

from finops_intelligence.economics import (
    TokenAssumptions, calculate_token_plan, gpu_cost_share, priority_signals
)


def inputs(**overrides):
    values = dict(
        inferences=100,
        input_tokens_per_inference=1000,
        output_tokens_per_inference=500,
        premium_input_per_million=Decimal("4"),
        premium_output_per_million=Decimal("10"),
        efficient_input_per_million=Decimal("1"),
        efficient_output_per_million=Decimal("2"),
        efficient_share_pct=50,
        retry_overhead_pct=10,
        volume_growth_pct=0,
    )
    values.update(overrides)
    return TokenAssumptions(**values)


class TokenEconomicsTest(unittest.TestCase):
    def test_blended_price_with_retry_overhead(self):
        result = calculate_token_plan(inputs())
        self.assertEqual(result["planning_inferences"], Decimal("100"))
        self.assertEqual(result["assumed_input_tokens"], Decimal("100000"))
        self.assertEqual(result["assumed_output_tokens"], Decimal("50000"))
        self.assertEqual(result["blended_input_rate"], Decimal("2.5"))
        self.assertEqual(result["blended_output_rate"], Decimal("6"))
        self.assertEqual(result["input_cost"], Decimal("0.25"))
        self.assertEqual(result["output_cost"], Decimal("0.30"))
        self.assertEqual(result["retry_cost"], Decimal("0.06"))
        self.assertEqual(result["total_cost"], Decimal("0.61"))
        self.assertEqual(result["cost_per_thousand_primary_inferences"], Decimal("6.05"))

    def test_efficiency_routing_reduces_assumed_cost(self):
        expensive = calculate_token_plan(inputs(efficient_share_pct=0))
        efficient = calculate_token_plan(inputs(efficient_share_pct=100))
        self.assertLess(efficient["total_cost"], expensive["total_cost"])

    def test_growth_scales_volume_and_not_historical_ledger(self):
        initial = calculate_token_plan(inputs(retry_overhead_pct=0))
        doubled = calculate_token_plan(inputs(retry_overhead_pct=0, volume_growth_pct=100))
        self.assertEqual(doubled["planning_inferences"], Decimal("200"))
        self.assertEqual(doubled["total_cost"], initial["total_cost"] * 2)

    def test_no_inferences_no_token_cost(self):
        zero = calculate_token_plan(inputs(inferences=0))
        self.assertEqual(zero["total_cost"], Decimal("0.00"))
        self.assertEqual(zero["cost_per_thousand_primary_inferences"], Decimal("0"))

    def test_reject_invalid_input(self):
        for invalid in [
            {"inferences": -1},
            {"input_tokens_per_inference": -10},
            {"efficient_share_pct": 101},
            {"retry_overhead_pct": -1},
            {"volume_growth_pct": 301},
            {"premium_input_per_million": Decimal("NaN")},
            {"efficient_output_per_million": Decimal("-1")},
        ]:
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    inputs(**invalid)

    def test_gpu_cost_share(self):
        share = gpu_cost_share(Decimal("25829.78"), Decimal("94410.59"))
        self.assertGreater(share, Decimal("27"))
        self.assertLess(share, Decimal("28"))
        with self.assertRaises(ValueError):
            gpu_cost_share(Decimal("120"), Decimal("100"))

    def test_signals_separate_actual_evidence_from_scenario(self):
        signals = priority_signals(
            gpu_share_pct=Decimal("27.36"),
            modeled_token_cost=Decimal("2700"),
            planning_limit=Decimal("2500"),
            retry_overhead_pct=25,
        )
        names = {signal["name"] for signal in signals}
        self.assertEqual(len(signals), 5)
        self.assertIn("No measured token charges", names)
        self.assertIn("GPU cost concentration", names)
        self.assertIn("Modeled token plan above planning limit", names)
        self.assertIn("High assumed retry overhead", names)
        self.assertTrue(all("next_step" in signal for signal in signals))

    def test_invalid_planning_limit(self):
        with self.assertRaises(ValueError):
            priority_signals(
                gpu_share_pct=Decimal("10"),
                modeled_token_cost=Decimal("0"),
                planning_limit=Decimal("0"),
                retry_overhead_pct=0,
            )


if __name__ == "__main__":
    unittest.main()
