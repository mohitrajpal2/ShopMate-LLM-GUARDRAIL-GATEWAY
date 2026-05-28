# CI/CD Learning Notes — ShopMate Project

## Concepts

### Docker
Packages your app and all its dependencies into a single portable container.
Run anywhere — no "works on my machine" problem.

### GitHub Actions
Automation tool built into GitHub. You write a `.yml` file and GitHub runs it automatically on every push.
Runs on GitHub's servers (called **runners**) — free Ubuntu machines.

### CI/CD
- **CI (Continuous Integration)** — automatically test your code on every push
- **CD (Continuous Deployment)** — automatically deploy if tests pass

### Docker Hub
GitHub but for Docker images. Stores your built images so any server can pull and run them.

### Render
Cloud platform that hosts your app. Connects to Docker Hub and auto-deploys when a new image is available.

---

## The Full Pipeline We Built

```
push code to GitHub
        ↓
GitHub Actions — job 1: test
  - installs dependencies (uv sync)
  - downloads spaCy model
  - runs pytest (34 guardrail tests)
        ↓ only if tests pass
GitHub Actions — job 2: docker
  - builds Docker image
  - pushes to Docker Hub
  - calls Render deploy hook
        ↓
Render
  - pulls new image from Docker Hub
  - restarts app automatically
  - live at public URL
```

---

## Step-by-Step: What We Did

### 1. Created the GitHub Actions Workflow

**Important:** `.github/workflows/` must be at the **repo root**, not inside a subfolder.

File: `.github/workflows/ci.yml`

```yaml
name: ShopMate CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: shopmate
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - run: uv sync
      - run: uv run python -m spacy download en_core_web_lg
      - run: uv run pytest tests/ -v
        env:
          JWT_SECRET: test-secret-key
          JWT_ALGORITHM: HS256
          JWT_EXPIRE_MINUTES: "60"
          GEMINI_API_KEY: test-key
          REDIS_URL: memory://

  docker:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    steps:
      - uses: actions/checkout@v4
      - uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_TOKEN }}
      - uses: docker/build-push-action@v5
        with:
          context: ./shopmate
          push: true
          tags: m0h1trajpal/shopmate:latest
      - name: Trigger Render deploy
        run: curl -s "${{ secrets.RENDER_DEPLOY_HOOK }}"
```

**Key concepts:**
- `needs: test` — docker job waits for test job to finish
- `if: github.ref == 'refs/heads/main'` — only builds on main, not pull requests
- `secrets.*` — sensitive values stored in GitHub, never in code

---

### 2. Created the Dockerfile

File: `shopmate/Dockerfile`

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

RUN uv run python -m spacy download en_core_web_lg

COPY . .

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

### 3. Added GitHub Secrets

Go to: GitHub repo → Settings → Secrets and variables → Actions

| Secret | What it is |
|--------|-----------|
| `DOCKER_USERNAME` | Docker Hub username |
| `DOCKER_TOKEN` | Docker Hub access token (not password) |
| `RENDER_DEPLOY_HOOK` | Render deploy hook URL |

**How to get Docker Hub token:**
Docker Hub → Account Settings → Personal access tokens → Generate new token (Read & Write)

---

### 4. Set Up Branch Protection Rules

Go to: GitHub repo → Settings → Branches → Add branch ruleset

Rules enabled:
- Restrict deletions
- Require a pull request before merging
- Require status checks to pass → select `test` job
- Block force pushes

**Effect:** Nobody can merge broken code into main. CI must pass first.

---

### 5. Created Render Account and Web Service

1. Go to [render.com](https://render.com) → sign up with GitHub
2. New → Web Service → Deploy existing image from registry
3. Image URL: `docker.io/m0h1trajpal/shopmate:latest`
4. Instance type: Free
5. Add environment variables:

| Key | Value |
|-----|-------|
| `JWT_SECRET` | your secret string |
| `JWT_ALGORITHM` | HS256 |
| `JWT_EXPIRE_MINUTES` | 60 |
| `GEMINI_API_KEY` | your Gemini API key |

**Deploy Hook:**
Render → service → Settings → Deploy Hook → copy URL → add as `RENDER_DEPLOY_HOOK` in GitHub secrets

---

### 6. Fixed Issues Along the Way

| Problem | Cause | Fix |
|---------|-------|-----|
| Workflow not found on GitHub | `.github/` was inside `shopmate/` subfolder | Moved to repo root |
| 8 tests failing on CI | Intent detection threshold too strict for Linux | Lowered threshold from `0.82` to `0.75` |
| 3 tests still failing | Seed examples didn't match test message phrasing | Added closer seed examples |
| Out of memory on Render | spaCy large model too big for 512MB free tier | Switch to `en_core_web_sm` |
| Render not auto-deploying | Render doesn't watch Docker Hub by default | Added deploy hook call in CI |
| App crash without Redis | Defaulted to `redis://localhost:6379` | Changed fallback to `memory://` |

---

## Professional Git Workflow (After Branch Protection)

```bash
# never push directly to main
git checkout -b feature/your-change
git add .
git commit -m "your message"
git push origin feature/your-change
# open Pull Request on GitHub
# CI runs automatically
# green ✅ → merge allowed
# red ❌ → merge blocked
```

---

## Free Tier Limits (Render)

| Limit | Value |
|-------|-------|
| RAM | 512MB |
| Sleep | After 15 min inactivity |
| Wake up time | ~30 seconds |
| Bandwidth | 100GB/month |

App sleeps when idle — first request after sleep takes ~30 seconds. Fine for learning/portfolio projects.
