import json
import os

from .policy_engine import get_role_policy

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def _load(filename: str) -> list[dict]:
    with open(os.path.join(_DATA_DIR, filename)) as f:
        return json.load(f)


def check_role_topic(message: str, role: str) -> tuple[bool, str | None]:
    """Returns (allowed, reason). Checks blocked_topics and blocked_actions from policy."""
    policy = get_role_policy(role)
    msg_lower = message.lower()

    for topic in policy.get("blocked_topics", []):
        if any(word in msg_lower for word in topic.split()):
            return False, f"Blocked topic: {topic}"

    for action in policy.get("blocked_actions", []):
        if any(word in msg_lower for word in action.split()):
            return False, f"Blocked action: {action}"

    return True, None


def scope_customer_data(customer_id: str, requested_customer_id: str | None) -> tuple[bool, str | None]:
    """Ensures a customer can only access their own data."""
    if requested_customer_id and requested_customer_id != customer_id:
        return False, "You can only access your own order data."
    return True, None


def scope_seller_data(seller_id: str, message: str) -> tuple[bool, str | None]:
    """Blocks seller queries about other sellers or platform-wide data."""
    competitor_keywords = ["competitor", "other seller", "top seller", "platform average", "rival", "other store"]
    msg_lower = message.lower()
    if any(kw in msg_lower for kw in competitor_keywords):
        return False, "You can only access your own store data."
    return True, None


def check_seller_product_ownership(seller_id: str, product_id: str) -> tuple[bool, str | None]:
    """Verifies the seller owns the product they're referencing."""
    products = _load("products.json")
    product = next((p for p in products if p["product_id"] == product_id), None)
    if not product:
        return False, "Product not found."
    if product["seller_id"] != seller_id:
        return False, "You can only access your own products."
    return True, None
