"""Shipping fees. Orders at or above the threshold ship free."""

from __future__ import annotations

from decimal import Decimal

from shop.money import quantize

FREE_SHIPPING_THRESHOLD = Decimal("50.00")
FLAT_FEE = Decimal("4.90")


def shipping_fee(subtotal: Decimal) -> Decimal:
    """Free shipping when subtotal reaches (>=) the threshold."""
    if subtotal >= FREE_SHIPPING_THRESHOLD:
        return Decimal("0.00")
    return quantize(FLAT_FEE)
