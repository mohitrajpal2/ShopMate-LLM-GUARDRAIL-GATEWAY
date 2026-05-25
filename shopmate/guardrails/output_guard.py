import re
from typing import Optional

from presidio_analyzer import AnalyzerEngine

_analyzer = AnalyzerEngine()

# Discount code pattern: alphanumeric codes 4-20 chars, often ALL_CAPS or with dashes
_DISCOUNT_CODE_PATTERN = re.compile(
    r"\b([A-Z]{2,}[0-9]{2,}|[A-Z0-9]{4,20}(?:[-_][A-Z0-9]+)*)\b"
)

_INTERNAL_FIELD_PATTERNS = [
    re.compile(r"\b(XXXX-XXXX-\d{4})\b"),          # bank account mask
    re.compile(r"\b([A-Z]{4}0\d{6})\b"),             # IFSC code
    re.compile(r"demand_trend|stock_level|internal_pricing"),
]

_SAFE_DISCOUNT_RESPONSE = "I can't share internal promotion details. Check the offers page."


def _contains_discount_codes(text: str) -> bool:
    """Heuristic: flag if response contains patterns that look like promo codes."""
    matches = _DISCOUNT_CODE_PATTERN.findall(text)
    # Filter out common non-code uppercase words
    _COMMON_WORDS = {"HTTP", "URL", "API", "FAQ", "ID", "OK", "USD", "INR", "SKU"}
    suspicious = [m for m in matches if m not in _COMMON_WORDS and len(m) >= 5]
    return len(suspicious) > 0


def _contains_internal_fields(text: str) -> bool:
    return any(p.search(text) for p in _INTERNAL_FIELD_PATTERNS)


def _contains_pii(text: str) -> bool:
    results = _analyzer.analyze(text=text, language="en")
    return len(results) > 0


def check_output(response: str) -> tuple[bool, Optional[str], Optional[str]]:
    """
    Returns (is_safe, blocked_response, reason).
    If safe: (True, None, None)
    If blocked: (False, safe_message, reason)
    """
    if _contains_discount_codes(response):
        return False, _SAFE_DISCOUNT_RESPONSE, "Output contained discount code patterns"

    if _contains_internal_fields(response):
        return False, "I can't share that internal information.", "Output contained internal data fields"

    if _contains_pii(response):
        return False, "I can't share personal information in this response.", "Output contained PII"

    return True, None, None
