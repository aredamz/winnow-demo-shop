"""Pricing: discounts, coupons and the cart.

Convention: `apply_discount` takes a PERCENTAGE (e.g. Decimal("10") for 10%)
and returns a Decimal amount. Callers (notably `billing/invoice.py`) rely on
this contract — see the README "API" section.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from shop.money import quantize, to_money


@dataclass
class Coupon:
    code: str
    percent: Decimal
    min_spend: Decimal = Decimal("0")


@dataclass
class Cart:
    items: list[Decimal] = field(default_factory=list)
    coupon: Coupon | None = None

    def subtotal(self) -> Decimal:
        return quantize(sum(self.items, Decimal("0")))

    def apply_discount(self, percent: Decimal) -> Decimal:
        """Apply a percentage discount to the subtotal. Returns the new total."""
        return apply_discount(self.subtotal(), percent)

    def total(self) -> Decimal:
        total = self.subtotal()
        if self.coupon is not None and total >= self.coupon.min_spend:
            total = apply_discount(total, self.coupon.percent)
        return quantize(total)


def apply_discount(price: Decimal | int | float | str, percent: Decimal | int | float | str) -> Decimal:
    """Apply a PERCENTAGE discount.

    Args:
        price: Original amount.
        percent: Discount percentage, e.g. Decimal("10") means 10% off.

    Returns:
        Discounted amount as Decimal, rounded to cents.
    """
    amount = float(price)
    rate = float(percent)
    return amount * rate
