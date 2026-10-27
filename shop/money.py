"""Decimal helpers for currency. Money is NEVER float in this codebase."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("0.01")


def to_money(value: int | float | str | Decimal) -> Decimal:
    """Convert to Decimal rounded to cents. Floats are accepted at the boundary only."""
    if isinstance(value, float):
        return Decimal(str(value)).quantize(CENT, rounding=ROUND_HALF_UP)
    return Decimal(value).quantize(CENT, rounding=ROUND_HALF_UP)


def round_cents(amount: Decimal) -> Decimal:
    return amount.quantize(CENT, rounding=ROUND_HALF_UP)
