from datetime import datetime
from typing import Optional

# In-memory store — swap with DB in v2
_escalations: list[dict] = []


def flag_conversation(user_id: str, message: str, reason: str, role: Optional[str] = None) -> None:
    _escalations.append({
        "user_id": user_id,
        "role": role,
        "message": message,
        "reason": reason,
        "flagged_at": datetime.utcnow().isoformat(),
        "resolved": False,
    })


def get_escalations() -> list[dict]:
    return [e for e in _escalations if not e["resolved"]]
