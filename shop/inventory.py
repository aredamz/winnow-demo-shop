"""Async stock reservation. All reservations go through `reserve_stock`."""

from __future__ import annotations

import asyncio

_STOCK: dict[str, int] = {}
_LOCK = asyncio.Lock()


def set_stock(sku: str, quantity: int) -> None:
    _STOCK[sku] = quantity


def stock_of(sku: str) -> int:
    return _STOCK.get(sku, 0)


async def reserve_stock(sku: str, quantity: int) -> bool:
    """Reserve units. Returns False when stock is insufficient. Must be awaited."""
    async with _LOCK:
        await asyncio.sleep(0)  # yield so concurrent reservations serialise on the lock
        available = _STOCK.get(sku, 0)
        if available < quantity:
            return False
        _STOCK[sku] = available - quantity
        return True


async def release_stock(sku: str, quantity: int) -> None:
    async with _LOCK:
        _STOCK[sku] = _STOCK.get(sku, 0) + quantity
