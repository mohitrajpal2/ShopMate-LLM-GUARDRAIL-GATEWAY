import json
import os
from datetime import datetime, timedelta
from pathlib import Path

import bcrypt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET", "fallback-secret-change-me")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

_USERS_PATH = Path(__file__).parent.parent / "data" / "users.json"
_bearer = HTTPBearer()


def _load_users() -> list[dict]:
    with open(_USERS_PATH) as f:
        return json.load(f)


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


def create_token(user: dict) -> str:
    payload = {
        "sub": user["user_id"],
        "role": user["role"],
        "seller_id": user.get("seller_id"),
        "exp": datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def login(request: LoginRequest) -> TokenResponse:
    users = _load_users()
    user = next((u for u in users if u["email"] == request.email), None)
    if not user or not bcrypt.checkpw(request.password.encode(), user["password_hash"].encode()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return TokenResponse(access_token=create_token(user))


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(_bearer)) -> dict:
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return {
            "user_id": payload["sub"],
            "role": payload["role"],
            "seller_id": payload.get("seller_id"),
        }
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")


def require_role(*roles: str):
    def _check(user: dict = Depends(get_current_user)) -> dict:
        if user["role"] not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user
    return _check
