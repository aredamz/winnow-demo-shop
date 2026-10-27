"""SQLite access. All queries are parameterised (see shop/orders.py)."""

from __future__ import annotations

import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY,
    user_name TEXT NOT NULL,
    status TEXT NOT NULL,
    total TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id),
    sku TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    price TEXT NOT NULL
);
"""


def connect(path: str = ":memory:") -> sqlite3.Connection:
    # Demo-grade: one shared connection across TestClient threads.
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.executescript(SCHEMA)
    return conn


def add_item(conn: sqlite3.Connection, order_id: int, sku: str, quantity: int, price: str) -> None:
    conn.execute(
        "INSERT INTO order_items (order_id, sku, quantity, price) VALUES (?, ?, ?, ?)",
        (order_id, sku, quantity, price),
    )
    conn.commit()


def items_for_order(conn: sqlite3.Connection, order_id: int) -> list[tuple]:
    return conn.execute(
        "SELECT sku, quantity, price FROM order_items WHERE order_id = ? ORDER BY id",
        (order_id,),
    ).fetchall()
