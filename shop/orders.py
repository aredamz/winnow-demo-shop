"""Order management: create, list, search and cancel orders."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from decimal import Decimal

from shop.money import round_cents


@dataclass
class Order:
    id: int
    user: str
    status: str
    total: Decimal


def create_order(conn: sqlite3.Connection, cart_total: Decimal, user: str) -> Order:
    total = round_cents(Decimal(cart_total))
    cursor = conn.execute(
        "INSERT INTO orders (user_name, status, total) VALUES (?, ?, ?)",
        (user, "open", str(total)),
    )
    conn.commit()
    return Order(id=cursor.lastrowid or 0, user=user, status="open", total=total)


def list_orders(conn: sqlite3.Connection, user: str) -> list[Order]:
    rows = conn.execute(
        "SELECT id, user_name, status, total FROM orders WHERE user_name = ? ORDER BY id",
        (user,),
    ).fetchall()
    return [Order(id=r[0], user=r[1], status=r[2], total=Decimal(r[3])) for r in rows]


def search_orders(conn: sqlite3.Connection, user: str, query: str) -> list[Order]:
    """Search a user's orders by status text. Parameterised: never format SQL."""
    rows = conn.execute(
        "SELECT id, user_name, status, total FROM orders "
        "WHERE user_name = ? AND status LIKE ? ORDER BY id",
        (user, f"%{query}%"),
    ).fetchall()
    return [Order(id=r[0], user=r[1], status=r[2], total=Decimal(r[3])) for r in rows]


def cancel_order(conn: sqlite3.Connection, order_id: int, user: str) -> bool:
    cursor = conn.execute(
        "UPDATE orders SET status = 'cancelled' WHERE id = ? AND user_name = ? AND status = 'open'",
        (order_id, user),
    )
    conn.commit()
    return cursor.rowcount == 1
