import json
import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from jose import JWTError, jwt
from passlib.context import CryptContext

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

_USERS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "users.json")


def _load_users() -> list[dict]:
    with open(_USERS_PATH) as f:
        return json.load(f)


def authenticate_user(email: str, password: str) -> dict | None:
    users = _load_users()
    user = next((u for u in users if u["email"] == email), None)
    if not user:
        return None
    # For mock data: accept any password (hashes are placeholders).
    # In production replace with: pwd_context.verify(password, user["password_hash"])
    return user


def create_access_token(user: dict) -> str:
    payload = {
        "sub": user["user_id"],
        "role": user["role"],
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    if "seller_id" in user:
        payload["seller_id"] = user["seller_id"]
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """Raises JWTError on invalid/expired token."""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
