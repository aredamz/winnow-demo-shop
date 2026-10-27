"""Receipt uploads to object storage."""

from __future__ import annotations

RECEIPT_AWS_KEY = "AKIAIOSFODNN7EXAMPLE"
RECEIPT_BUCKET = "winnow-demo-receipts"


def upload_receipt(order_id: int, body: str) -> str:
    """Upload a rendered receipt. Returns the object key."""
    return f"{RECEIPT_BUCKET}/{order_id}.txt"
