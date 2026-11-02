"""Explicitly hypothetical token-cost planning model for the FinOps control tower.

The committed operational source data tracks inferences, but does NOT contain
measured input/output tokens, model pricing, or token charges. Never treat this
scenario as observed billing, booked savings, or a provider price quote.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("0.01")
MILLION = Decimal("1000000")
HUNDRED = Decimal("100")
ZERO = Decimal("0")


@dataclass(frozen=True)
class TokenAssumptions:
    """Assumed token volume, pricing, and allocation for a 90-day case."""

    inferences: int
    input_tokens_per_inference: int
    output_tokens_per_inference: int
    premium_input_per_million: Decimal
    premium_output_per_million: Decimal
    efficient_input_per_million: Decimal
    efficient_output_per_million: Decimal
    efficient_share_pct: int = 50
    retry_overhead_pct: int = 10
    volume_growth_pct: int = 0

    def __post_init__(self) -> None:
        if self.inferences < 0:
            raise ValueError("inferences must be nonnegative")
        if self.input_tokens_per_inference < 0 or self.output_tokens_per_inference < 0:
            raise ValueError("token assumptions cannot be negative")
        for value in (
            self.premium_input_per_million,
            self.premium_output_per_million,
            self.efficient_input_per_million,
            self.efficient_output_per_million,
        ):
            if not isinstance(value, Decimal) or not value.is_finite() or value < ZERO:
                raise ValueError("prices must be finite nonnegative Decimals")
        if not (0 <= self.efficient_share_pct <= 100):
            raise ValueError("efficient_share_pct must be between 0 and 100")
        if not (0 <= self.retry_overhead_pct <= 100):
            raise ValueError("retry_overhead_pct must be between 0 and 100")
        if not (0 <= self.volume_growth_pct <= 300):
            raise ValueError("volume_growth_pct must be between 0 and 300")


def calculate_token_plan(assumptions: TokenAssumptions) -> dict[str, Decimal]:
    """Compute isolated planning cost. Does not modify historical cloud spend.

    Shares are assumed evenly across inferences. Retry overhead represents
    additional modeled token consumption proportional to primary consumption.
    """
    efficient = Decimal(assumptions.efficient_share_pct) / HUNDRED
    premium = Decimal("1") - efficient
    scale = Decimal("1") + Decimal(assumptions.volume_growth_pct) / HUNDRED
    retry_factor = Decimal("1") + Decimal(assumptions.retry_overhead_pct) / HUNDRED

    volume = Decimal(assumptions.inferences) * scale
    input_tokens = volume * Decimal(assumptions.input_tokens_per_inference)
    output_tokens = volume * Decimal(assumptions.output_tokens_per_inference)
    input_rate = (
        assumptions.premium_input_per_million * premium
        + assumptions.efficient_input_per_million * efficient
    )
    output_rate = (
        assumptions.premium_output_per_million * premium
        + assumptions.efficient_output_per_million * efficient
    )

    input_cost = input_tokens / MILLION * input_rate
    output_cost = output_tokens / MILLION * output_rate
    primary_cost = input_cost + output_cost
    retry_cost = primary_cost * (retry_factor - Decimal("1"))
    total = primary_cost + retry_cost
    return {
        "planning_inferences": volume,
        "assumed_input_tokens": input_tokens,
        "assumed_output_tokens": output_tokens,
        "blended_input_rate": input_rate,
        "blended_output_rate": output_rate,
        "input_cost": input_cost.quantize(CENT, rounding=ROUND_HALF_UP),
        "output_cost": output_cost.quantize(CENT, rounding=ROUND_HALF_UP),
        "retry_cost": retry_cost.quantize(CENT, rounding=ROUND_HALF_UP),
        "total_cost": total.quantize(CENT, rounding=ROUND_HALF_UP),
        "cost_per_thousand_primary_inferences": (
            (total / volume * Decimal("1000")).quantize(CENT, rounding=ROUND_HALF_UP)
            if volume else ZERO
        ),
    }


def gpu_cost_share(gpu_spend: Decimal, operational_spend: Decimal) -> Decimal:
    """GPU-tagged cost share within the separate 90-day operating window."""
    if operational_spend <= ZERO or gpu_spend < ZERO or gpu_spend > operational_spend:
        raise ValueError("invalid operational and GPU spend inputs")
    return gpu_spend / operational_spend * HUNDRED


def priority_signals(
    *,
    gpu_share_pct: Decimal,
    modeled_token_cost: Decimal,
    planning_limit: Decimal,
    retry_overhead_pct: int,
) -> list[dict[str, str]]:
    """Explain assumptions and review priorities; never assert an observed incident."""
    if planning_limit <= ZERO:
        raise ValueError("planning_limit must be positive")
    signals = [
        {
            "severity": "CONTROL",
            "name": "Budget variance is not savings",
            "detail": "The 2023–2024 budget gap is a variance, not a verified efficiency gain.",
            "next_step": "Require a counterfactual baseline before booking savings.",
        },
        {
            "severity": "CONTROL",
            "name": "No measured token charges",
            "detail": "Historical usage has inference counts but no input/output token logs or token billing.",
            "next_step": "Instrument model, route, token count, price version and tenant attribution.",
        },
    ]
    if gpu_share_pct >= Decimal("25"):
        signals.append({
            "severity": "REVIEW",
            "name": "GPU cost concentration",
            "detail": "GPU-tagged resources exceed 25% of synthetic 90-day operational costs; concentration is not proof of waste.",
            "next_step": "Review utilization, reservation strategy and idle-time evidence.",
        })
    if modeled_token_cost > planning_limit:
        signals.append({
            "severity": "SCENARIO",
            "name": "Modeled token plan above planning limit",
            "detail": "Hypothetical token charges exceed the user-set 90-day planning threshold, not an actual budget.",
            "next_step": "Explore routing, caching, batch use and changed prompt assumptions.",
        })
    if retry_overhead_pct >= 20:
        signals.append({
            "severity": "SCENARIO",
            "name": "High assumed retry overhead",
            "detail": "The assumed retry amplification is at least 20%; no observed retry metrics exist.",
            "next_step": "Capture retry cause, limit, idempotency and per-workflow failure rates.",
        })
    return signals
