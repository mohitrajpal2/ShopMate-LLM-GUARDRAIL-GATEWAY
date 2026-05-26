# ShopMate — Code Understanding Index

This is the teaching plan. We go file by file, concept by concept.
Each topic has a `completed` flag. Flip it to `true` after we cover it in a session.

---

## Module 1 — How a Request Flows Through the System (Big Picture)

**What we cover:**
- What happens from the moment a user sends a message to when they get a response
- The 4 stages: Auth → Input Guard → LLM → Output Guard
- Why each stage exists and what it protects against
- How `main.py` is the conductor that calls everything else

```
completed = true
```

---

## Module 2 — Project Structure & Entry Point (`main.py`)

**What we cover:**
- What FastAPI is and why we use it
- What `app = FastAPI(...)` does — creating the server
- What an endpoint is (`@app.post`, `@app.get`)
- What `Depends()` means — dependency injection in FastAPI
- What middleware is and why `attach_user_state` runs before every request
- What `request.state` is — how we pass data between middleware and endpoints
- The 4 endpoints: `/auth/login`, `/health`, `/chat`, `/escalations`
- How the `/chat` endpoint calls the full pipeline in order

```
completed = true
```

---

## Module 3 — Authentication (`auth/jwt_handler.py`)

**What we cover:**
- What a JWT token is — structure, what's inside it (sub, role, seller_id, exp)
- Why we use tokens instead of passwords on every request
- `create_token()` — how we pack user data into a signed token
- `login()` — how we verify email + password and return a token
- `bcrypt.checkpw()` — why passwords are stored as hashes, never plain text
- `get_current_user()` — how every protected endpoint reads the token
- `require_role()` — how we lock endpoints to specific roles (support_agent only)
- What 401 vs 403 means and when each is returned

```
completed = false
```

---

## Module 4 — Policy Engine (`guardrails/policy_engine.py`)

**What we cover:**
- What a YAML policy file is and why it exists (non-engineers can edit rules)
- How `load_policy()` reads the YAML into a Python dict
- What `internal_data.never_expose` means and how it drives the output guard
- How changing the YAML changes behavior without touching any Python code

```
completed = false
```

---

## Module 5 — Intent Detection (`guardrails/intent_detector.py`)

**What we cover:**
- What sentence-transformers does — turning text into numbers (vectors)
- What ChromaDB is — a vector database that stores those numbers
- What semantic similarity means — why "I want to fake a defect" matches "claim a defect to get refund"
- The 8 threat categories seeded into the collection
- `_seed_collection()` — why we seed once and reuse
- `detect_intent()` — how we query ChromaDB and convert L2 distance to similarity score
- What the threshold (0.82) means — tuning sensitivity

```
completed = false
```

---

## Module 6 — Input Guard (`guardrails/input_guard.py`)

**What we cover:**
- What `GuardResult` dataclass is — the standard return shape for all guardrail checks
- The pipeline order: financial mutation → competitor query → semantic intent → keyword fallback
- Why order matters — financial mutation check runs first for all roles
- The difference between `allowed=False` (block) and `flag_reason` set (flag + respond)
- How Problems 1, 3, 4, 5, 6, 7, 8 are handled here
- Keyword fallbacks — why we have both semantic AND keyword checks

```
completed = false
```

---

## Module 7 — Role Guard (`guardrails/role_guard.py`)

**What we cover:**
- `check_customer_order_access()` — how we enforce a customer can only see their own orders
- `check_seller_product_access()` — how we enforce a seller can only see their own products
- `is_competitor_query()` — keyword list that catches Problem 3
- `is_financial_mutation_request()` — keyword list that catches Problem 7
- `get_seller_scoped_products()` and `get_customer_scoped_orders()` — data scoping helpers

```
completed = false
```

---

## Module 8 — Output Guard (`guardrails/output_guard.py`)

**What we cover:**
- Why we need to check the LLM's response — the LLM can leak internal data
- `_contains_discount_codes()` — regex pattern matching for promo code shapes
- `_contains_internal_fields()` — catching bank account masks, IFSC codes, internal field names
- `_contains_pii()` — how Presidio + spaCy scans for names, emails, phone numbers
- `check_output()` — the three-layer output scan and what it returns
- How Problem 2 (discount fishing) is caught at the output layer

```
completed = false
```

---

## Module 9 — Gemini Client (`llm/gemini_client.py`)

**What we cover:**
- What LangChain is — why we use it as an orchestration wrapper over Gemini
- `SystemMessage` vs `HumanMessage` — how we give the LLM its persona and the user's message
- `_SYSTEM_PROMPT` — why we tell the LLM to never reveal internal data (defense in depth)
- `get_response()` — the async call to Gemini
- Why `ainvoke` is used instead of `invoke` — async vs sync

```
completed = false
```

---

## Module 10 — Retry Logic (`core/retry.py`)

**What we cover:**
- Why external API calls need retry logic — network failures, rate limits
- `retry_async()` — how exponential backoff works (1s → 2s → 4s)
- What `TypeVar` is used for here
- When it gives up and raises the error

```
completed = false
```

---

## Module 11 — Escalation (`core/escalation.py`)

**What we cover:**
- What escalation means in this system — flagging for human review
- `flag_conversation()` — what data gets stored and why
- `get_escalations()` — why we filter `resolved=False`
- Why this is in-memory for v1 and what changes in v2 (database)
- How Problems 5 and 8 trigger this

```
completed = false
```

---

## Module 12 — Tests (`tests/test_shopmate_guardrails.py`)

**What we cover:**
- Why we mock the LLM — tests must be fast and not need a real API key
- `TestClient` — how FastAPI lets us test endpoints without running a real server
- `create_token()` in tests — generating tokens directly without going through login
- How each test class maps to one of the 8 guardrail problems
- What `patch("main.get_response")` does — replacing the real function with a fake one
- How to read a test assertion and understand what it proves

```
completed = false
```

---

## Module 13 — Mock Data (`data/*.json`)

**What we cover:**
- Why mock data exists — simulates a real database without needing one
- `products.json` structure — what each field means and which ones are INTERNAL
- `orders.json` — how customer_id links orders to users
- `sellers.json` — what bank_account and pending_payout represent
- `users.json` — role field, seller_id field, password_hash

```
completed = false
```

---

## Module 14 — End to End Walkthrough (Putting It All Together)

**What we cover:**    Input Guard
- Walk through a real attack message step by step through every layer
- Walk through a legitimate message step by step
- Draw the full data flow on paper
- Understand what would break if you removed each layer

```
completed = false
```
