"""Pricing and invoice tests. Green on main; seeded PRs must keep them green."""

from decimal import Decimal

import pytest

from billing.invoice import Invoice
from shop.money import to_money
from shop.pricing import Cart, Coupon, apply_discount


def test_apply_discount_percent() -> None:
    assert apply_discount(Decimal("100"), Decimal("10")) == Decimal("90.00")


def test_apply_discount_rejects_out_of_range() -> None:
    with pytest.raises(ValueError):
        apply_discount(Decimal("100"), Decimal("150"))


def test_money_never_float() -> None:
    assert isinstance(to_money("10.005"), Decimal)
    assert isinstance(apply_discount(100, 10), Decimal)


def test_cart_coupon_with_min_spend() -> None:
    cart = Cart(items=[Decimal("60"), Decimal("60")], coupon=Coupon("SAVE10", Decimal("10")))
    assert cart.total() == Decimal("108.00")
    poor = Cart(items=[Decimal("5")], coupon=Coupon("SAVE10", Decimal("10"), Decimal("50")))
    assert poor.total() == Decimal("5.00")


def test_invoice_total_uses_percent() -> None:
    invoice = Invoice(lines=[Decimal("100")], discount_percent=Decimal("10"))
    assert invoice.total() == Decimal("90.00")
    assert invoice.line_count() == 1
