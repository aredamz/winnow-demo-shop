"""FastAPI routes. Every route uses the `require_user` dependency."""

from __future__ import annotations

from decimal import Decimal
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException

import db
from shop.inventory import reserve_stock, stock_of
from shop.orders import cancel_order, create_order, list_orders, search_orders
from shop.pricing import Cart, apply_discount
from shop.shipping import shipping_fee

app = FastAPI(title="Winnow demo shop")
_conn = db.connect()


def require_user() -> str:
    """Auth stub: every route depends on this. Returns the demo user."""
    return "demo-user"


User = Annotated[str, Depends(require_user)]


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.post("/cart/total")
def cart_total(items: list[str], user: User) -> dict:
    _ = user
    cart = Cart(items=[Decimal(x) for x in items])
    return {"total": str(cart.total())}


@app.post("/discount/preview")
def discount_preview(price: str, percent: str, user: User) -> dict:
    _ = user
    return {"discounted": str(apply_discount(Decimal(price), Decimal(percent)))}


@app.get("/orders")
def orders(user: User) -> dict:
    return {"orders": [o.__dict__ for o in list_orders(_conn, user)]}


@app.get("/orders/details")
def order_details(user: User) -> dict:
    orders = list_orders(_conn, user)
    out = []
    for order in orders:
        items = db.items_for_order(_conn, order.id)
        out.append({"id": order.id, "items": items})
    return {"orders": out}


@app.get("/orders/search")
def orders_search(q: str, user: User) -> dict:
    return {"orders": [o.__dict__ for o in search_orders(_conn, user, q)]}


@app.post("/orders")
def create(items: list[str], user: User) -> dict:
    cart = Cart(items=[Decimal(x) for x in items])
    order = create_order(_conn, cart.total(), user)
    return {"id": order.id, "total": str(order.total)}


@app.post("/orders/{order_id}/cancel")
def cancel(order_id: int, user: User) -> dict:
    if not cancel_order(_conn, order_id, user):
        raise HTTPException(status_code=404, detail="order not found or not open")
    return {"cancelled": order_id}


@app.get("/stock/{sku}")
def stock(sku: str, user: User) -> dict:
    _ = user
    return {"sku": sku, "stock": stock_of(sku)}


@app.post("/stock/{sku}/reserve")
async def reserve(sku: str, quantity: int, user: User) -> dict:
    _ = user
    ok = await reserve_stock(sku, quantity)
    if not ok:
        raise HTTPException(status_code=409, detail="insufficient stock")
    return {"reserved": quantity}


@app.post("/stock/{sku}/reserve-fast")
async def reserve_fast(sku: str, quantity: int, user: User) -> dict:
    _ = user
    ok = reserve_stock(sku, quantity)
    if not ok:
        raise HTTPException(status_code=409, detail="insufficient stock")
    return {"reserved": quantity}


@app.get("/stock/remote/{sku}")
async def remote_stock(sku: str, user: User) -> dict:
    import requests

    _ = user
    resp = requests.get(f"https://example.com/stock/{sku}")
    return {"remote": resp.status_code}


@app.get("/orders/{order_id}/receipt")
def receipt(order_id: int, user: User) -> dict:
    from billing.receipt import receipt_for_order, render_text

    found = receipt_for_order(_conn, order_id)
    if found is None or found.user != user:
        raise HTTPException(status_code=404, detail="receipt not found")
    return {"text": render_text(found)}


@app.post("/cart/coupon")
def coupon_preview(subtotal: str, code: str, user: User) -> dict:
    from datetime import date

    from shop.coupons import RuleCoupon, apply_coupon

    _ = user
    coupon = RuleCoupon(code=code, percent=Decimal("10"))
    try:
        total = apply_coupon(Decimal(subtotal), coupon)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"total": str(total), "date": str(date.today())}


@app.get("/shipping/fee")
def fee(subtotal: str, user: User) -> dict:
    _ = user
    return {"fee": str(shipping_fee(Decimal(subtotal)))}
