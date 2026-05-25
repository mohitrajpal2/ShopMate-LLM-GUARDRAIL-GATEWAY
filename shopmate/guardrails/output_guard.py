import re

from presidio_analyzer import AnalyzerEngine

_analyzer = AnalyzerEngine()

# Discount code pattern: uppercase alphanumeric 4-12 chars (e.g. SAVE20, STAFF50OFF)
_DISCOUNT_CODE_PATTERN = re.compile(r"\b[A-Z0-9]{4,12}\b")

# Internal field keywords that should never appear in output
_INTERNAL_KEYWORDS = [
    "discount_code", "stock_level", "demand_trend",
    "bank_account", "internal_pricing", "payout_balance",
    "seller_bank", "XXXX-HIDDEN",
]


def check_output(response_text: str) -> tuple[bool, str | None]:
    """
    Returns (clean, reason).
    clean=True means the response is safe to send.
    clean=False means it must be blocked.
    """
    # Block if internal field names leaked
    lower = response_text.lower()
    for kw in _INTERNAL_KEYWORDS:
        if kw.lower() in lower:
            return False, f"Internal data field leaked: {kw}"

    # Block if discount code pattern detected in output
    # Heuristic: uppercase token + context words nearby
    discount_context = re.compile(
        r"(code|coupon|promo|discount|offer)[^\n]{0,40}[A-Z0-9]{4,12}|[A-Z0-9]{4,12}[^\n]{0,40}(code|coupon|promo|discount)",
        re.IGNORECASE,
    )
    if discount_context.search(response_text):
        return False, "Blocked output: discount code pattern detected"

    # PII check via Presidio
    results = _analyzer.analyze(text=response_text, language="en")
    pii_types = {r.entity_type for r in results if r.score >= 0.7}
    if pii_types:
        return False, f"PII detected in output: {', '.join(pii_types)}"

    return True, None
