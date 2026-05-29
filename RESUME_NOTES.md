# Resume Notes — ShopMate Project

## Project Title
**ShopMate — LLM Guardrails Gateway**

---

## One Line Description (for resume header)
> Built a production-grade AI chat assistant for fashion e-commerce with an 8-category guardrails pipeline blocking prompt injection, PII leakage, and social engineering attacks.

---

## Resume Bullet Points (Projects Section)

- Designed and implemented a **guardrails middleware layer** for a Gemini-powered chat assistant, blocking 8 attack categories including price manipulation, return fraud, PII leakage, and emotional manipulation
- Built **semantic intent detection** using ChromaDB and sentence-transformers to classify malicious user intent with configurable similarity thresholds
- Integrated **Microsoft Presidio + spaCy** for real-time PII detection and blocking before messages reach the LLM
- Implemented **role-based access control** (customer / seller / support agent) with JWT authentication and per-role rate limiting via Redis
- Engineered a **policy-driven architecture** using YAML config, allowing guardrail rules to be updated without code changes
- Set up a **full CI/CD pipeline** using GitHub Actions — automated testing (34 pytest cases), Docker image build, Docker Hub push, and Render auto-deployment on every merge to main
- Wrote **34 pytest test cases** covering all 8 guardrail problems, auth flows, role access, and customer data isolation

---

## Skills Section — What To Add

### AI / LLM
- LLM Guardrails & Safety
- Prompt Injection Defense
- Semantic Search (ChromaDB)
- Sentence Transformers
- LangChain
- Gemini API

### Backend
- FastAPI
- REST API Design
- JWT Authentication
- Rate Limiting
- Python

### Data & NLP
- PII Detection (Microsoft Presidio)
- spaCy
- Vector Embeddings

### DevOps & CI/CD
- GitHub Actions
- Docker
- Docker Hub
- CI/CD Pipelines
- Render (Cloud Deployment)

### Testing
- pytest
- Unit Testing
- Mocking (unittest.mock)

---

## What Makes This Project Stand Out On a Resume

| What You Built | Why It Matters |
|----------------|---------------|
| Guardrails layer | LLM safety is one of the hottest topics in AI right now |
| Semantic intent detection | Shows you understand vector search and embeddings |
| CI/CD pipeline | Shows you think beyond just writing code |
| 34 test cases | Shows you write production-quality code |
| Policy-driven YAML config | Shows you think about maintainability |
| Role-based access | Shows you understand real-world security |

---

## How To Describe It In Interviews

**"What did you build?"**
> A FastAPI backend that sits between users and a Gemini LLM. Every message passes through a guardrails pipeline that detects and blocks 8 categories of attacks — from price manipulation to emotional manipulation — before they reach the model.

**"What was the hardest part?"**
> Getting semantic intent detection to work consistently across different environments. The similarity scores from sentence-transformers varied between Windows and Linux, causing tests to pass locally but fail in CI. I fixed it by tuning the threshold and adding more representative seed examples.

**"What did you learn?"**
> How to build a full CI/CD pipeline from scratch — automated testing, Docker image builds, and cloud deployment on every code push. Also learned how LLM safety works in production beyond just prompt engineering.
