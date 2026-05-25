# ShopMate — LLM Guardrails Gateway

An AI-powered chat assistant for a fashion e-commerce platform, backed by Gemini and protected by a production-grade guardrails layer that blocks 8 categories of attacks automatically.

---

## What It Does

ShopMate sits between the user and the Gemini LLM. Every request and response passes through a guardrails pipeline that enforces:

- Role-based access (customer / seller / support agent)
- PII detection and blocking
- Semantic intent detection (price manipulation, return fraud, threats, etc.)
- Internal data classification (discount codes, inventory levels never exposed)
- Rate limiting per role
- Human escalation flagging for threats and emotional manipulation

---

## Tech Stack

| Layer | Tool |
|---|---|
| LLM | Gemini API (gemini-2.5-flash) |
| Backend | FastAPI |
| Auth | JWT (python-jose) |
| PII Detection | Microsoft Presidio + spaCy |
| Semantic Search | ChromaDB + sentence-transformers |
| Rate Limiting | slowapi (Redis-backed) |
| Orchestration | LangChain |
| Package Manager | uv |
| Container | Docker (Redis only) |

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- [uv](https://astral.sh/uv) installed
- Gemini API key from [aistudio.google.com](https://aistudio.google.com)

---

## Setup & Run

### 1. Clone and enter the project

```bash
cd ShopMate-LLM-GUARDRAIL-GATEWAY/shopmate
```

### 2. Configure environment variables

Edit `.env` and fill in your values:

```env
JWT_SECRET=any-long-random-string-you-choose
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60
GEMINI_API_KEY=your-actual-gemini-api-key
REDIS_URL=redis://localhost:6379
SENTENCE_TRANSFORMERS_HOME=./.cache/sentence_transformers
```

### 3. Start Redis

```bash
docker-compose up -d
```

### 4. Install Python dependencies

```bash
uv sync
```

> First run takes 3–5 minutes — downloads sentence-transformers, chromadb, presidio, etc.

### 5. Download the spaCy language model

```bash
uv run python -m spacy download en_core_web_lg
```

> This is required by Presidio for PII detection. It downloads spaCy's large English model which understands names, emails, phone numbers, and addresses in text. Only needed once.

### 6. Generate password hashes for mock users

All mock users share the password `secret`. Run this once to generate the bcrypt hash and update `data/users.json`:

```bash
uv run python -c "from passlib.context import CryptContext; print(CryptContext(schemes=['bcrypt']).hash('secret'))"
```

Copy the output and replace all `password_hash` values in `data/users.json` with it.

### 7. Run the app

```bash
uv run uvicorn main:app --reload
```

App runs at: `http://localhost:8000`
Swagger UI at: `http://localhost:8000/docs`

---

## Run Tests

```bash
uv run pytest tests/ -v
```

---

## API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/auth/login` | None | Get JWT token |
| GET | `/health` | None | Server status |
| POST | `/chat` | JWT | Main guardrailed chat |
| GET | `/escalations` | JWT (support only) | View flagged conversations |

### Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "priya@example.com", "password": "secret"}'
```

### Chat

```bash
curl -X POST http://localhost:8000/chat \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the return policy for dresses?"}'
```

---

## Mock Users

| Email | Password | Role |
|---|---|---|
| priya@example.com | secret | customer |
| arjun@example.com | secret | customer |
| riya@fashions.com | secret | seller (S001) |
| trendy@threads.com | secret | seller (S002) |
| kavya@shopmate.com | secret | support_agent |

---

## The 8 Guardrail Problems

| # | Problem | Guardrail Type | Action |
|---|---|---|---|
| 1 | Price Manipulation | Semantic intent detection | Block |
| 2 | Discount Code Fishing | Output pattern blocking | Block |
| 3 | Seller Competitor Spying | Role-based data scoping | Block |
| 4 | Return Policy Abuse | Semantic intent detection | Block |
| 5 | Fake Urgency / Threats | Threat detection | Flag + safe response |
| 6 | Inventory Extraction | Data classification | Block |
| 7 | Seller Impersonation | Action guardrail | Block |
| 8 | Emotional Manipulation | Emotion detection | Flag + safe response |

---

## Project Structure

```
shopmate/
├── main.py                          # FastAPI entry point
├── config/
│   └── shopmate_policy.yaml         # All rules — edit here, no code change needed
├── auth/
│   └── jwt_handler.py               # Login + JWT creation + validation
├── guardrails/
│   ├── input_guard.py               # All input checks
│   ├── output_guard.py              # All output checks
│   ├── role_guard.py                # Role-based access checks
│   ├── intent_detector.py           # Semantic intent detection (ChromaDB)
│   └── policy_engine.py             # Loads shopmate_policy.yaml
├── llm/
│   └── gemini_client.py             # Gemini wrapper
├── core/
│   ├── retry.py                     # Retry + fallback logic
│   └── escalation.py                # Flags conversations for human review
├── data/
│   ├── products.json
│   ├── orders.json
│   ├── sellers.json
│   └── users.json
├── tests/
│   └── test_shopmate_guardrails.py  # All 8 problems tested
├── docker-compose.yml               # Redis only
├── pyproject.toml
└── .env
```
