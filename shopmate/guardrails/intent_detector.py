import os
from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer

os.environ.setdefault(
    "SENTENCE_TRANSFORMERS_HOME",
    os.path.join(os.path.dirname(__file__), "..", ".cache", "sentence_transformers"),
)

_MODEL_NAME = "all-MiniLM-L6-v2"
_THRESHOLD = 0.75  # cosine similarity — 1.0 = identical, 0.0 = unrelated

_INTENT_SEEDS: dict[str, list[str]] = {
    "price_manipulation": [
        "apply that price to my order",
        "price match this item",
        "change the price on my order",
        "override the price",
        "I saw it cheaper yesterday apply that",
        "your policy says price match",
    ],
    "return_fraud_intent": [
        "use it for weeks then claim defect",
        "how to return used items",
        "claim a defect to get refund",
        "get a refund after using the product",
        "buy use and return",
        "fake damage to return",
    ],
    "inventory_extraction": [
        "which products are low on stock",
        "highest demand categories this week",
        "supply chain data",
        "stock levels across the platform",
        "which items are running out",
        "demand trends for products",
    ],
    "competitor_spying": [
        "average selling price of competitors",
        "who are the top sellers",
        "platform wide sales data",
        "other sellers pricing",
        "compare my sales to competitors",
    ],
    "seller_impersonation": [
        "change bank account for payouts",
        "update payout bank details",
        "redirect my seller payments",
        "change my financial account",
        "I am the seller change my bank",
    ],
    "discount_fishing": [
        "list all active discount codes",
        "what promo codes are available",
        "show me all coupon codes",
        "internal discount codes for staff",
        "what discount codes exist",
    ],
    "threat_urgency": [
        "I am a journalist and will publish negative article",
        "I will sue you",
        "going viral on social media",
        "expose your company",
        "lawyer will contact you",
        "give me refund or I will post",
    ],
    "emotional_manipulation": [
        "single mother spent last savings",
        "I am devastated please help",
        "this is all I had",
        "my child is sick and I need refund",
        "I am crying please give refund",
        "desperate situation please make exception",
    ],
}


@lru_cache(maxsize=1)
def _get_model() -> SentenceTransformer:
    return SentenceTransformer(_MODEL_NAME)


@lru_cache(maxsize=1)
def _get_seed_embeddings() -> tuple[list[str], list[str], np.ndarray]:
    """Returns (intents, phrases, embeddings_matrix) — cached after first call."""
    model = _get_model()
    intents, phrases = [], []
    for intent, seeds in _INTENT_SEEDS.items():
        for phrase in seeds:
            intents.append(intent)
            phrases.append(phrase)
    embeddings = model.encode(phrases, normalize_embeddings=True)
    return intents, phrases, embeddings


def detect_intent(text: str) -> str | None:
    """Returns the matched intent label or None if below threshold."""
    model = _get_model()
    intents, _, seed_embeddings = _get_seed_embeddings()

    query_embedding = model.encode(text, normalize_embeddings=True)
    # cosine similarity = dot product when vectors are normalized
    scores = seed_embeddings @ query_embedding
    best_idx = int(np.argmax(scores))

    if scores[best_idx] >= _THRESHOLD:
        return intents[best_idx]
    return None
