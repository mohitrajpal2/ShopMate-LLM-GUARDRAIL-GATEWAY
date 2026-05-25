from .intent_detector import detect_intent
from .role_guard import check_role_topic, scope_seller_data

# Financial mutation keywords for Problem 7
_FINANCIAL_KEYWORDS = [
    "bank account", "payout", "change account", "update account",
    "redirect payment", "financial account", "change bank",
]

# Inventory/supply keywords for Problem 6
_INVENTORY_KEYWORDS = [
    "low on stock", "out of stock", "stock level", "demand this week",
    "highest demand", "supply chain", "inventory", "demand trend",
]

# Discount code pattern for Problem 2 (input side)
_DISCOUNT_INPUT_KEYWORDS = [
    "discount code", "promo code", "coupon code", "active codes",
    "list all codes", "what codes",
]

_BLOCK_RESPONSES = {
    "price_manipulation": "Price changes require verification. Please contact support.",
    "return_fraud_intent": "I can share our return policy. Returns are subject to quality verification.",
    "inventory_extraction": "Stock availability is shown on each product page. I can't share inventory data.",
    "competitor_spying": "You can only access your own store data.",
    "seller_impersonation": "Financial account changes must be done through the verified seller portal with 2FA.",
    "discount_fishing": "I can't share internal promotion details. Check the offers page.",
}

_ESCALATION_RESPONSES = {
    "threat_urgency": "I understand your concern. I'm connecting you to a senior support agent who can help resolve this.",
    "emotional_manipulation": "I'm really sorry to hear this. Here's how to raise a return request: shopmate.com/returns. I'm also flagging this for a support agent to follow up with you personally.",
}


def check_input(message: str, user: dict) -> dict | None:
    """
    Returns a guardrail result dict if the input should be blocked or escalated,
    or None if the input is clean and should proceed to the LLM.

    Result shape: {"success": bool, "response": str, "flagged": bool, "reason": str}
    """
    role = user["role"]
    msg_lower = message.lower()

    # --- Problem 7: Financial mutation (block before anything else) ---
    if any(kw in msg_lower for kw in _FINANCIAL_KEYWORDS):
        return {
            "success": False,
            "response": _BLOCK_RESPONSES["seller_impersonation"],
            "flagged": False,
            "reason": "Blocked action: financial mutation in chat",
        }

    # --- Problem 6: Inventory extraction keywords ---
    if any(kw in msg_lower for kw in _INVENTORY_KEYWORDS):
        return {
            "success": False,
            "response": _BLOCK_RESPONSES["inventory_extraction"],
            "flagged": False,
            "reason": "Blocked topic: inventory levels",
        }

    # --- Problem 2: Discount code fishing (input side) ---
    if any(kw in msg_lower for kw in _DISCOUNT_INPUT_KEYWORDS):
        return {
            "success": False,
            "response": _BLOCK_RESPONSES["discount_fishing"],
            "flagged": False,
            "reason": "Blocked topic: internal discount codes",
        }

    # --- Role-based topic/action blocking ---
    allowed, reason = check_role_topic(message, role)
    if not allowed:
        return {
            "success": False,
            "response": "I'm sorry, I cannot help with that.",
            "flagged": False,
            "reason": reason,
        }

    # --- Seller competitor scoping (Problem 3) ---
    if role == "seller":
        seller_id = user.get("seller_id", "")
        allowed, reason = scope_seller_data(seller_id, message)
        if not allowed:
            return {
                "success": False,
                "response": _BLOCK_RESPONSES["competitor_spying"],
                "flagged": False,
                "reason": reason,
            }

    # --- Semantic intent detection (Problems 1, 4, 5, 8) ---
    intent = detect_intent(message)

    if intent in _BLOCK_RESPONSES:
        return {
            "success": False,
            "response": _BLOCK_RESPONSES[intent],
            "flagged": False,
            "reason": f"Blocked intent: {intent}",
        }

    if intent in _ESCALATION_RESPONSES:
        if intent in ("threat_urgency", "emotional_manipulation"):
            return {
                "success": True,
                "response": _ESCALATION_RESPONSES[intent],
                "flagged": True,
                "reason": f"{intent.replace('_', ' ').title()} detected",
            }

    return None
