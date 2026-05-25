import re
from dataclasses import dataclass
from typing import Optional

from guardrails.intent_detector import detect_intent
from guardrails.role_guard import is_competitor_query, is_financial_mutation_request


@dataclass
class GuardResult:
    allowed: bool
    block_reason: Optional[str] = None
    flag_reason: Optional[str] = None
    safe_response: Optional[str] = None


_INVENTORY_KEYWORDS = [
    "low on stock", "out of stock", "stock level", "inventory",
    "demand trend", "highest demand", "supply chain", "restock",
    "how many left", "stock count",
]

_DISCOUNT_INPUT_KEYWORDS = [
    "discount code", "promo code", "coupon code", "voucher code",
    "active codes", "promotion code", "offer code",
]


def check_input(message: str, role: str, seller_id: Optional[str] = None) -> GuardResult:
    """
    Runs all input guardrails in order. Returns on first match.
    Pipeline: financial mutation → competitor query → semantic intent → keyword checks
    """
    msg_lower = message.lower()

    # Problem 7 — Seller impersonation / financial mutation (all roles)
    if is_financial_mutation_request(message):
        return GuardResult(
            allowed=False,
            block_reason="Financial account changes blocked in chat",
            safe_response="Financial account changes must be done through the verified seller portal with 2FA.",
        )

    # Problem 3 — Seller competitor spying
    if role == "seller" and is_competitor_query(message):
        return GuardResult(
            allowed=False,
            block_reason="Competitor data query blocked",
            safe_response="You can only access your own store data.",
        )

    # Semantic intent detection
    intent = detect_intent(message)

    if intent == "price_manipulation":
        return GuardResult(
            allowed=False,
            block_reason="Price manipulation attempt detected",
            safe_response="Price changes require verification. Please contact support.",
        )

    if intent == "return_fraud":
        return GuardResult(
            allowed=False,
            block_reason="Return fraud intent detected",
            safe_response="I can share our return policy. Returns are subject to quality verification.",
        )

    if intent == "inventory_extraction":
        return GuardResult(
            allowed=False,
            block_reason="Inventory data extraction blocked",
            safe_response="Stock availability is shown on each product page. I can't share inventory data.",
        )

    if intent == "competitor_spying":
        return GuardResult(
            allowed=False,
            block_reason="Competitor data query blocked",
            safe_response="You can only access your own store data.",
        )

    if intent == "threat_urgency":
        return GuardResult(
            allowed=True,
            flag_reason="Threat or urgency social engineering detected",
            safe_response="I understand your concern. I'm connecting you to a senior support agent who can help resolve this.",
        )

    if intent == "emotional_manipulation":
        return GuardResult(
            allowed=True,
            flag_reason="Emotional manipulation detected",
            safe_response="I'm really sorry to hear this. Here's how to raise a return request at shopmate.com/returns. I'm also flagging this for a support agent to follow up with you personally.",
        )

    if intent == "seller_impersonation":
        return GuardResult(
            allowed=False,
            block_reason="Seller impersonation / financial mutation blocked",
            safe_response="Financial account changes must be done through the verified seller portal with 2FA.",
        )

    if intent == "discount_fishing":
        return GuardResult(
            allowed=False,
            block_reason="Internal discount code request blocked",
            safe_response="I can't share internal promotion details. Check the offers page.",
        )

    # Keyword fallbacks for inventory and discount fishing
    if any(kw in msg_lower for kw in _INVENTORY_KEYWORDS):
        return GuardResult(
            allowed=False,
            block_reason="Inventory data extraction blocked",
            safe_response="Stock availability is shown on each product page. I can't share inventory data.",
        )

    if any(kw in msg_lower for kw in _DISCOUNT_INPUT_KEYWORDS):
        return GuardResult(
            allowed=False,
            block_reason="Internal discount code request blocked",
            safe_response="I can't share internal promotion details. Check the offers page.",
        )

    return GuardResult(allowed=True)
