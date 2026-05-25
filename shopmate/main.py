import os
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt as jose_jwt
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from limits import parse as parse_limit
from limits.storage import storage_from_string
from limits.strategies import MovingWindowRateLimiter

from auth.jwt_handler import authenticate_user, create_access_token, decode_token
from core.escalation import flag_conversation, get_all_escalations
from guardrails.input_guard import check_input
from guardrails.output_guard import check_output
from llm.gemini_client import call_gemini

load_dotenv()

_REDIS_URL = os.getenv("REDIS_URL", "memory://")
_JWT_SECRET = os.getenv("JWT_SECRET")
_ALGORITHM = "HS256"

# Per-role rate limits
_ROLE_LIMITS = {
    "customer": parse_limit("20/minute"),
    "seller": parse_limit("30/minute"),
    "support_agent": parse_limit("60/minute"),
}

_storage = storage_from_string(_REDIS_URL)
_rate_limiter = MovingWindowRateLimiter(_storage)

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="ShopMate Guardrails Gateway")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

security = HTTPBearer()


class LoginRequest(BaseModel):
    email: str
    password: str


class ChatRequest(BaseModel):
    message: str


def get_current_user(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]) -> dict:
    try:
        return decode_token(credentials.credentials)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")


def _enforce_rate_limit(user_id: str, role: str) -> None:
    limit = _ROLE_LIMITS.get(role, _ROLE_LIMITS["customer"])
    key = f"shopmate:{role}:{user_id}"
    if not _rate_limiter.hit(limit, key):
        raise HTTPException(status_code=429, detail=f"Rate limit exceeded for role: {role}")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/auth/login")
def login(body: LoginRequest):
    user = authenticate_user(body.email, body.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return {"access_token": create_access_token(user), "token_type": "bearer"}


@app.post("/chat")
async def chat(
    request: Request,
    body: ChatRequest,
    user: Annotated[dict, Depends(get_current_user)],
):
    role = user.get("role", "customer")
    user_id = user.get("sub", "unknown")

    _enforce_rate_limit(user_id, role)

    guard_result = check_input(body.message, user)
    if guard_result:
        if guard_result.get("flagged"):
            flag_conversation(user_id, body.message, guard_result["reason"])
        return guard_result

    try:
        llm_response = await call_gemini(body.message)
    except Exception:
        raise HTTPException(status_code=503, detail="LLM service unavailable")

    clean, reason = check_output(llm_response)
    if not clean:
        return {
            "success": False,
            "response": "I'm sorry, I cannot share that information.",
            "flagged": False,
            "reason": reason,
        }

    return {"success": True, "response": llm_response, "flagged": False, "reason": None}


@app.get("/escalations")
def escalations(user: Annotated[dict, Depends(get_current_user)]):
    if user.get("role") != "support_agent":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Support agents only")
    return get_all_escalations()
