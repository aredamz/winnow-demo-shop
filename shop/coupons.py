"""Coupon rules: expiry, usage caps and stacking.

A coupon applies when ALL of these hold:
- today is within [starts_at, ends_at],
- uses_so_far is below max_uses,
- the cart subtotal reaches min_spend,
- no other coupon is already applied (no stacking).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass
class RuleCoupon:
    code: str
    percent: Decimal
    min_spend: Decimal = Decimal("0")
    starts_at: date | None = None
    ends_at: date | None = None
    max_uses: int = 1_000_000
    uses_so_far: int = 0


def coupon_valid(coupon: RuleCoupon, subtotal: Decimal, today: date | None = None) -> bool:
    """Check every rule. Pure function so tests pin the behaviour."""
    day = today or date.today()
    if coupon.starts_at is not None and day < coupon.starts_at:
        return False
    if coupon.ends_at is not None and day > coupon.ends_at:
        return False
    if coupon.uses_so_far >= coupon.max_uses:
        return False
    return subtotal >= coupon.min_spend


def apply_coupon(
    subtotal: Decimal, coupon: RuleCoupon | None, already_discounted: bool = False
) -> Decimal:
    """Apply at most one coupon. Raises when stacking is attempted."""
    from shop.pricing import apply_discount

    if coupon is None:
        return subtotal
    if already_discounted:
        raise ValueError("coupons do not stack")
    if not coupon_valid(coupon, subtotal):
        raise ValueError(f"coupon {coupon.code} is not valid for {subtotal}")
    coupon.uses_so_far += 1
    return apply_discount(subtotal, coupon.percent)
