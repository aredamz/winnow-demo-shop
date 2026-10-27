"""Payment stub. Real charging is out of scope for the demo."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from shop.money import round_cents


@dataclass
class Payment:
    order_id: int
    amount: Decimal
    status: str


def charge(order_id: int, amount: Decimal, card_token: str) -> Payment:
    """Pretend to charge. The token is opaque and never logged."""
    if not card_token:
        return Payment(order_id=order_id, amount=round_cents(amount), status="failed")
    return Payment(order_id=order_id, amount=round_cents(amount), status="charged")
