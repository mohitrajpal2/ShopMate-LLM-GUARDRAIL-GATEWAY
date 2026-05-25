from datetime import datetime

_escalations: list[dict] = []


def flag_conversation(user_id: str, message: str, reason: str) -> None:
    _escalations.append({
        "user_id": user_id,
        "message": message,
        "reason": reason,
        "flagged_at": datetime.utcnow().isoformat(),
    })


def get_all_escalations() -> list[dict]:
    return list(_escalations)
