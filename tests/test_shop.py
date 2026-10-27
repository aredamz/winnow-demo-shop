"""Coupon, receipt and pagination tests. Green on main."""

from datetime import date
from decimal import Decimal

import pytest

import db
from billing.receipt import create_full_order, receipt_for_order, render_text
from shop.coupons import RuleCoupon, apply_coupon, coupon_valid
from shop.orders import create_order, list_orders


def _coupon(**overrides) -> RuleCoupon:
    base = {"code": "SAVE10", "percent": Decimal("10")}
    base.update(overrides)
    return RuleCoupon(**base)  # type: ignore[arg-type]


def test_coupon_expiry_and_cap() -> None:
    assert coupon_valid(_coupon(), Decimal("100"), date(2026, 6, 1))
    assert not coupon_valid(
        _coupon(starts_at=date(2026, 7, 1)), Decimal("100"), date(2026, 6, 1)
    )
    assert not coupon_valid(
        _coupon(ends_at=date(2026, 5, 1)), Decimal("100"), date(2026, 6, 1)
    )
    assert not coupon_valid(_coupon(max_uses=1, uses_so_far=1), Decimal("100"))
    assert not coupon_valid(_coupon(min_spend=Decimal("50")), Decimal("10"))


def test_coupon_no_stacking_and_single_use_count() -> None:
    coupon = _coupon()
    assert apply_coupon(Decimal("100"), coupon) == Decimal("90.00")
    assert coupon.uses_so_far == 1
    with pytest.raises(ValueError):
        apply_coupon(Decimal("100"), _coupon(), already_discounted=True)
    with pytest.raises(ValueError):
        apply_coupon(Decimal("1"), _coupon(min_spend=Decimal("50")))


def test_receipt_single_query() -> None:
    conn = db.connect()
    order_id = create_full_order(
        conn, "mei", [("SKU-1", 2, "10.00"), ("SKU-2", 1, "5.00")], "25.00"
    )
    receipt = receipt_for_order(conn, order_id)
    assert receipt is not None and len(receipt.lines) == 2
    assert receipt.total == Decimal("25.00")
    text = render_text(receipt)
    assert "SKU-1 x2" in text and "Total: 25.00" in text
    assert receipt_for_order(conn, 9999) is None


def test_order_pagination_ordering() -> None:
    conn = db.connect()
    ids = [create_order(conn, Decimal(i), "faiz").id for i in range(1, 4)]
    got = [o.id for o in list_orders(conn, "faiz")]
    assert got == ids  # insertion order, oldest first
