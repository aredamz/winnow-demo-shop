"""Invoices. `Invoice.total` relies on `apply_discount` percent semantics."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from shop.money import quantize
from shop.pricing import apply_discount


@dataclass
class Invoice:
    lines: list[Decimal]
    discount_percent: Decimal = Decimal("0")

    def subtotal(self) -> Decimal:
        return quantize(sum(self.lines, Decimal("0")))

    def total(self) -> Decimal:
        """Total after the percentage discount (percent, NOT a fraction)."""
        if self.discount_percent == 0:
            return self.subtotal()
        return apply_discount(self.subtotal(), self.discount_percent)

    def line_count(self) -> int:
        return len(self.lines)
