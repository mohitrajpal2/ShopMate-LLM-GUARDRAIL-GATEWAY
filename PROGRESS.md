# ShopMate — Learning Progress

Use this file at the start of every new session to know exactly where we left off.
Update it at the end of every session before closing.

---

## Current Status

**Last session:** Module 2 — main.py and FastAPI basics
**Next session starts at:** Module 3 — Authentication (`auth/jwt_handler.py`)

---

## Completed Topics

| Module | Topic | Date Completed | Key Takeaway |
|--------|-------|----------------|--------------|
| Module 2 | Project Structure & Entry Point (`main.py`) | Day 1 | FastAPI, endpoints, Depends(), middleware, request.state, the /chat pipeline order |
| Module 1 | How a Request Flows Through the System | Day 1 | 4 stages: Auth → Input Guard → LLM → Output Guard. Block vs Flag+Respond. main.py is the conductor. |
| — | Built the full project from spec | Day 1 | 14 files, 8 guardrails, FastAPI + Gemini + ChromaDB + Presidio |
| — | Fixed uv build backend error | Day 1 | `package = false` in pyproject.toml for flat script projects |
| — | Fixed passlib/bcrypt incompatibility | Day 1 | Replaced passlib with direct bcrypt library |
| — | Fixed langchain.schema import error | Day 1 | Moved to `langchain_core.messages` in LangChain v0.2+ |
| — | Generated real bcrypt password hash | Day 1 | All mock users use password: `secret` |

---

## Pending Topics

- Module 3 — JWT auth and bcrypt
- Module 4 — Policy engine and YAML
- Module 5 — Intent detection with ChromaDB + sentence-transformers
- Module 6 — Input guard pipeline
- Module 7 — Role guard and data scoping
- Module 8 — Output guard and Presidio PII detection
- Module 9 — Gemini client and LangChain
- Module 10 — Retry logic
- Module 11 — Escalation system
- Module 12 — Tests and mocking
- Module 13 — Mock data structure
- Module 14 — Full end-to-end walkthrough

---

## Concepts Learned So Far

- **Docker** — environment parity, runs Redis as external service
- **uv** — modern Python package manager, replaces pip + venv
- **bcrypt** — one-way password hashing, never store plain text passwords
- **JWT** — signed token carrying user identity and role, sent on every request
- **FastAPI** — Python web framework, auto-generates Swagger docs
- **spaCy en_core_web_lg** — large English NLP model used by Presidio for PII detection
- **Presidio** — Microsoft's PII detection library, runs locally
- **ChromaDB** — local vector database for semantic similarity search
- **sentence-transformers** — converts text to vectors (numbers) for similarity comparison

---

## How to Use This File

At the start of a new session, paste this into the chat:
> "I am continuing the ShopMate code walkthrough. Progress file says we are at [Module X]. Let's continue from there."

At the end of a session, update:
1. "Last session" date
2. "Next session starts at" module
3. Move completed modules from Pending to Completed table
4. Add any new concepts to "Concepts Learned"
