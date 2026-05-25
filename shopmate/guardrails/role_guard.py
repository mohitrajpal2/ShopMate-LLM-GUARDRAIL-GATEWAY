import json
from pathlib import Path
from typing import Optional

_ORDERS_PATH = Path(__file__).parent.parent / "data" / "orders.json"
_PRODUCTS_PATH = Path(__file__).parent.parent / "data" / "products.json"


def _load_json(path: Path) -> list[dict]:
    with open(path) as f:
        return json.load(f)


def check_customer_order_access(customer_id: str, order_id: str) -> bool:
    """Returns True only if the order belongs to this customer."""
    orders = _load_json(_ORDERS_PATH)
    order = next((o for o in orders if o["order_id"] == order_id), None)
    return order is not None and order["customer_id"] == customer_id


def check_seller_product_access(seller_id: str, product_id: str) -> bool:
    """Returns True only if the product belongs to this seller."""
    products = _load_json(_PRODUCTS_PATH)
    product = next((p for p in products if p["product_id"] == product_id), None)
    return product is not None and product["seller_id"] == seller_id


_COMPETITOR_KEYWORDS = [
    "competitor", "other seller", "top seller", "platform average",
    "platform wide", "other store", "rival", "compare seller",
]

_FINANCIAL_MUTATION_KEYWORDS = [
    "change bank", "update bank", "bank account", "payout account",
    "change payout", "update payout", "redirect payout", "financial details",
    "account number", "ifsc", "routing number",
]


def is_competitor_query(message: str) -> bool:
    msg = message.lower()
    return any(kw in msg for kw in _COMPETITOR_KEYWORDS)


def is_financial_mutation_request(message: str) -> bool:
    msg = message.lower()
    return any(kw in msg for kw in _FINANCIAL_MUTATION_KEYWORDS)


def get_seller_scoped_products(seller_id: str) -> list[dict]:
    products = _load_json(_PRODUCTS_PATH)
    return [p for p in products if p["seller_id"] == seller_id]


def get_customer_scoped_orders(customer_id: str) -> list[dict]:
    orders = _load_json(_ORDERS_PATH)
    return [o for o in orders if o["customer_id"] == customer_id]
