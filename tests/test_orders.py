"""Order, inventory and shipping tests. Green on main."""

import asyncio
from decimal import Decimal

import db
from shop.inventory import release_stock, reserve_stock, set_stock, stock_of
from shop.orders import cancel_order, create_order, list_orders, search_orders
from shop.payments import charge
from shop.shipping import shipping_fee


def _conn():
    return db.connect()


def test_order_lifecycle() -> None:
    conn = _conn()
    order = create_order(conn, Decimal("20"), "aina")
    assert order.status == "open"
    assert [o.id for o in list_orders(conn, "aina")] == [order.id]
    assert cancel_order(conn, order.id, "aina")
    assert not cancel_order(conn, order.id, "aina")  # already cancelled


def test_search_is_parameterised() -> None:
    conn = _conn()
    create_order(conn, Decimal("20"), "aina")
    assert len(search_orders(conn, "aina", "open")) == 1
    assert search_orders(conn, "aina", "' OR '1'='1") == []  # injection stays inert
    assert search_orders(conn, "faiz", "open") == []


def test_inventory_reserve_and_release() -> None:
    async def scenario() -> None:
        set_stock("SKU-1", 2)
        assert await reserve_stock("SKU-1", 2)
        assert not await reserve_stock("SKU-1", 1)
        await release_stock("SKU-1", 1)
        assert stock_of("SKU-1") == 1

    asyncio.run(scenario())


def test_payment_stub() -> None:
    ok = charge(1, Decimal("20"), "tok_123")
    assert ok.status == "charged" and ok.amount == Decimal("20.00")
    assert charge(2, Decimal("20"), "").status == "failed"


def test_free_shipping_threshold_inclusive() -> None:
    assert shipping_fee(Decimal("50.00")) == Decimal("0.00")
    assert shipping_fee(Decimal("49.99")) == Decimal("4.90")
