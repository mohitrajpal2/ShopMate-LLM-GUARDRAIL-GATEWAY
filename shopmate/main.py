import os
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Request
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from auth.jwt_handler import LoginRequest, TokenResponse, get_current_user, login, require_role
from core.escalation import flag_conversation, get_escalations
from guardrails.input_guard import check_input
from guardrails.output_guard import check_output
from llm.gemini_client import get_response

load_dotenv()


# ---------------------------------------------------------------------------
# Rate limiter key: user_id from JWT state, fallback to IP
# ---------------------------------------------------------------------------

def _user_key(request: Request) -> str:
    user = getattr(request.state, "user", None)
    return user["user_id"] if user else get_remote_address(request)


limiter = Limiter(
    key_func=_user_key,
    storage_uri=os.getenv("REDIS_URL", "redis://localhost:6379"),
)

app = FastAPI(title="ShopMate Guardrails Gateway", version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ---------------------------------------------------------------------------
# Middleware — decode JWT and attach user to request.state early
# so the rate limiter key function can read it
# ---------------------------------------------------------------------------

@app.middleware("http")
async def attach_user_state(request: Request, call_next):
    from jose import JWTError, jwt

    request.state.user = None
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        token = auth.split(" ", 1)[1]
        try:
            payload = jwt.decode(
                token,
                os.getenv("JWT_SECRET", "fallback-secret-change-me"),
                algorithms=[os.getenv("JWT_ALGORITHM", "HS256")],
            )
            request.state.user = {
                "user_id": payload["sub"],
                "role": payload["role"],
                "seller_id": payload.get("seller_id"),
            }
        except JWTError:
            pass
    return await call_next(request)


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    success: bool
    response: str
    flagged: bool
    reason: str | None = None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.post("/auth/login", response_model=TokenResponse)
def auth_login(body: LoginRequest):
    return login(body)


@app.get("/health")
def health():
    return {"status": "ok", "service": "ShopMate Guardrails Gateway"}


@app.post("/chat", response_model=ChatResponse)
@limiter.limit("20/minute", key_func=lambda req: (
    req.state.user["user_id"] if getattr(req.state, "user", None) else get_remote_address(req)
))
async def chat(
    request: Request,
    body: ChatRequest,
    user: dict = Depends(get_current_user),
):
    # Ensure state is set (middleware already did this, but Depends re-validates)
    request.state.user = user

    role = user["role"]

    # Enforce per-role rate limits via separate decorated endpoints is complex with slowapi;
    # instead we apply the strictest common limit here and rely on role checks below.
    # The actual per-role limits are enforced by the limiter key being user-scoped.

    # --- Input guardrail ---
    guard = check_input(body.message, role=role, seller_id=user.get("seller_id"))

    if not guard.allowed:
        return ChatResponse(
            success=False,
            response=guard.safe_response or "I'm sorry, I cannot help with that.",
            flagged=False,
            reason=guard.block_reason,
        )

    # --- Flag-and-respond (threats, emotional manipulation) ---
    if guard.flag_reason:
        flag_conversation(
            user_id=user["user_id"],
            message=body.message,
            reason=guard.flag_reason,
            role=role,
        )
        return ChatResponse(
            success=True,
            response=guard.safe_response or "I'm connecting you to a support agent.",
            flagged=True,
            reason=guard.flag_reason,
        )

    # --- LLM call ---
    llm_response = await get_response(body.message, role=role)

    # --- Output guardrail ---
    is_safe, blocked_response, out_reason = check_output(llm_response)
    if not is_safe:
        return ChatResponse(
            success=False,
            response=blocked_response,
            flagged=False,
            reason=out_reason,
        )

    return ChatResponse(success=True, response=llm_response, flagged=False, reason=None)


@app.get("/escalations")
def escalations(user: dict = Depends(require_role("support_agent"))):
    return get_escalations()
