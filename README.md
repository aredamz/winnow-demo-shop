# Winnow demo shop

Mini shop API built with FastAPI. Demo target for Winnow, an autonomous
review-and-docs crew powered by Meta's Muse Spark.

## Setup

```bash
pip install -r requirements.txt
pytest
uvicorn api.routes:app
```

## API

- `apply_discount(price, percent) -> Decimal`: apply a **percentage** discount
  (e.g. `Decimal("10")` means 10% off). Uses `Decimal`, never float.
- `Cart.total() -> Decimal`: subtotal with the coupon applied.
- `Invoice.total() -> Decimal`: total after the percentage discount.
- `GET /orders`, `GET /orders/search?q=`, `POST /orders`, `POST /orders/{id}/cancel`
- `POST /stock/{sku}/reserve` (async), `GET /shipping/fee?subtotal=`
