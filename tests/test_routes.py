"""Route tests via TestClient. Every route requires the auth dependency."""

from fastapi.testclient import TestClient

from api.routes import app

client = TestClient(app)


def test_health() -> None:
    assert client.get("/health").json() == {"ok": True}


def test_cart_total_and_discount_preview() -> None:
    assert client.post("/cart/total", json=["10.00", "20.00"]).json() == {"total": "30.00"}
    assert client.post(
        "/discount/preview", params={"price": "100", "percent": "10"}
    ).json() == {"discounted": "90.00"}


def test_order_crud_and_search() -> None:
    created = client.post("/orders", json=["15.00"]).json()
    assert "id" in created
    ids = [o["id"] for o in client.get("/orders").json()["orders"]]
    assert created["id"] in ids
    assert client.get("/orders/search", params={"q": "open"}).json()["orders"]
    assert client.post(f"/orders/{created['id']}/cancel").json() == {
        "cancelled": created["id"]
    }
    assert client.post("/orders/999999/cancel").status_code == 404


def test_stock_and_shipping() -> None:
    assert client.get("/stock/NOPE").json() == {"sku": "NOPE", "stock": 0}
    assert client.post("/stock/NOPE/reserve", params={"quantity": 1}).status_code == 409
    assert client.get("/shipping/fee", params={"subtotal": "50.00"}).json() == {"fee": "0.00"}


def test_receipt_and_coupon_routes() -> None:
    from billing.receipt import create_full_order

    from api.routes import _conn

    order_id = create_full_order(_conn, "demo-user", [("SKU-9", 1, "12.00")], "12.00")
    body = client.get(f"/orders/{order_id}/receipt").json()
    assert "SKU-9 x1" in body["text"]
    assert client.get("/orders/999999/receipt").status_code == 404
    preview = client.post("/cart/coupon", params={"subtotal": "100", "code": "SAVE10"}).json()
    assert preview["total"] == "90.00"
