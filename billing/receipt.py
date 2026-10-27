"""Receipts: render an order with items in one query (no N+1)."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from decimal import Decimal

import db


@dataclass
class ReceiptLine:
    sku: str
    quantity: int
    price: Decimal


@dataclass
class Receipt:
    order_id: int
    user: str
    lines: list[ReceiptLine]
    total: Decimal


def receipt_for_order(conn: sqlite3.Connection, order_id: int) -> Receipt | None:
    """Single JOIN query: order header plus all items at once."""
    rows = conn.execute(
        "SELECT o.user_name, o.total, i.sku, i.quantity, i.price "
        "FROM orders o LEFT JOIN order_items i ON i.order_id = o.id "
        "WHERE o.id = ? ORDER BY i.id",
        (order_id,),
    ).fetchall()
    if not rows:
        return None
    lines = [
        ReceiptLine(sku=r[2], quantity=r[3], price=Decimal(r[4]))
        for r in rows
        if r[2] is not None
    ]
    return Receipt(
        order_id=order_id, user=rows[0][0], lines=lines, total=Decimal(rows[0][1])
    )


def render_text(receipt: Receipt) -> str:
    parts = [f"Receipt #{receipt.order_id} for {receipt.user}"]
    for line in receipt.lines:
        parts.append(f"  {line.sku} x{line.quantity} @ {line.price}")
    parts.append(f"Total: {receipt.total}")
    return "\n".join(parts)


def create_full_order(
    conn: sqlite3.Connection, user: str, items: list[tuple[str, int, str]], total: str
) -> int:
    """Create an order plus its items atomically (one transaction)."""
    from shop.orders import create_order

    order = create_order(conn, Decimal(total), user)
    try:
        for sku, quantity, price in items:
            db.add_item(conn, order.id, sku, quantity, price)
    except Exception:
        conn.execute("DELETE FROM order_items WHERE order_id = ?", (order.id,))
        conn.execute("DELETE FROM orders WHERE id = ?", (order.id,))
        conn.commit()
        raise
    return order.id
