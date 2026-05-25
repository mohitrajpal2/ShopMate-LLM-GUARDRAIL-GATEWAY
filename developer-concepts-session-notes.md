# Developer Concepts — Session Notes

---

## 1. JWT (JSON Web Token)

### What it is
A JWT is a signed token that proves who you are. It's created at login and sent with every request.

### The Night Club Analogy
- **You** = the user
- **Bouncer at the door** = the `/auth/login` endpoint
- **Wristband** = the JWT token
- **Staff inside** = every protected endpoint (`/chat`, `/escalations`)

### How it works
1. You send email + password to `/auth/login`
2. Server checks `users.json`, creates a wristband (JWT) stamped with your name, role, and expiry
3. The wristband is sealed with `JWT_SECRET` — only the server has this ink
4. You send the wristband with every request
5. Server checks: is the ink genuine? is it expired? was it tampered with?
6. If any check fails → 401 Unauthorized

### Key rule
The server **never stores the token**. It just checks the ink (SECRET_KEY) every time. Change the secret → all existing tokens instantly invalid.

---

## 2. Password Hashing

### What a hash is
A one-way transformation of a password:
```
"mypassword123"  →  bcrypt  →  "$2b$12$KIXbHq..."
```
- Cannot be reversed
- If database is hacked, attacker sees only the hash — useless to them

### What a placeholder hash is
A fake hash that **looks** like a real bcrypt hash but was never generated from any real password. Used in mock data so the code structure is correct without real users.

### Real vs Mock flow
```
REAL:  User types password → bcrypt.verify(password, real_hash) → True/False
MOCK:  User types anything → skip verification entirely → always True
```

---

## 3. Environments (dev / staging / prod)

### What environments are
Three separate running instances of the same app:
```
Your laptop     → dev
A test server   → staging  
AWS / cloud     → prod (real users)
```
Same codebase, same Git repo — completely separate deployments with separate configs.

### Why different JWT secrets per environment
If the secret is the same everywhere, a token minted in dev works on prod too. A developer could impersonate any user on the live system.

With different secrets:
```
dev   → JWT_SECRET=abc123
prod  → JWT_SECRET=x9f2k...
```
A dev token is cryptographically invalid on prod.

### Where secrets live per environment
| Environment | Where JWT_SECRET lives |
|---|---|
| Dev | `.env` file |
| Staging | Server environment variables |
| Prod | AWS Secrets Manager / Parameter Store |

### Tools for secret management
| Tool | Use case |
|---|---|
| `.env` file | Local dev only |
| AWS Secrets Manager | Production on AWS |
| AWS SSM Parameter Store | Non-sensitive config on AWS |
| HashiCorp Vault | Enterprise secret management |
| Doppler / Infisical | Developer-friendly, syncs across environments |

---

## 4. Redis

### What it is
A separate standalone server (not part of Python) that stores data in memory. Used here for rate limiting — tracking how many requests each user has made per minute.

### Why it wasn't running
Redis is not installed by default. It's a separate program that needs to be installed and started independently, like a second server running alongside your app.

### How your app talks to Redis
```
FastAPI app  →  "has this user hit the rate limit?"  →  Redis on localhost:6379
Redis        →  "yes / no"                           →  FastAPI app
```

### memory:// vs redis://
| | `memory://` | `redis://` |
|---|---|---|
| Needs Redis installed | No | Yes |
| Works across multiple servers | No | Yes |
| Good for local dev | ✅ | overkill |
| Production | ❌ | ✅ |

---

## 5. Docker

### What it actually is
A lightweight virtual machine that runs a mini Linux environment on your machine. Not just isolation — it lets you run any server (Redis, Postgres, etc.) without installing it on Windows.

### The Fish Tank Analogy
- Docker = a fish tank sitting on your desk
- Your Windows machine = the desk
- `-p` flag = a pipe drilled through the glass connecting desk to tank
- Your app talks through that pipe to whatever is running inside

### The `-p` flag explained
```
-p 6379:6379
    ↑       ↑
your machine  container inside Docker
```
Windows receives traffic on port 6379 and forwards it into the container.

### Running Redis in Docker
```bash
docker run -d --name redis-shopmate -p 6379:6379 redis:7-alpine
```
Your app connects to `localhost:6379` — has no idea Redis is inside a container.

### Running Postgres in Docker
```bash
docker run -d --name pg -p 5432:5432 -e POSTGRES_PASSWORD=secret postgres:16
```
Connect from local code using `localhost:5432` — same trick.

---

## 6. Two Ways to Run Your Setup

### Way 1 — Everything in Docker
```
┌─────────────────────────────┐
│ Docker                      │
│  ┌──────────┐ ┌──────────┐  │
│  │ FastAPI  │ │  Redis   │  │
│  └──────────┘ └──────────┘  │
└─────────────────────────────┘
```
Use Docker Compose — one command starts everything.

### Way 2 — Code local, dependencies in Docker (current setup)
```
┌─────────────────┐     ┌──────────────────┐
│ Your Machine    │     │ Docker           │
│  python main.py │────▶│  Redis/Postgres  │
└─────────────────┘     └──────────────────┘
```
Run code locally for fast reloads and easy debugging. Spin up Redis/Postgres in Docker so you don't install them on Windows. **Most common pattern during development.**

---

## 7. Docker Compose

### What it is
A tool to define and run multiple containers with one command.

```yaml
services:
  app:
    build: .
    ports:
      - "8000:8000"
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

```bash
docker compose up   # starts everything
docker compose down # stops everything
```

### Important: container networking
Inside Docker Compose, containers find each other **by service name**, not `localhost`:
```
app connects to redis  →  redis://redis:6379   ✅
app connects to redis  →  redis://localhost:6379  ❌ (localhost = itself inside Docker)
```

---

## 8. Viewing Postgres Tables Running in Docker

### Option 1 — pgAdmin in Docker (browser-based)
```bash
docker run -d --name pgadmin -p 5050:80 \
  -e PGADMIN_DEFAULT_EMAIL=admin@admin.com \
  -e PGADMIN_DEFAULT_PASSWORD=admin \
  dpage/pgadmin4
```
Open `http://localhost:5050` in browser. Same UI as desktop pgAdmin.

When connecting to Postgres also in Docker — use the **service name** as host, not localhost.

### Option 2 — Local pgAdmin app (simplest)
Already have pgAdmin on Windows? Just connect to:
```
host: localhost
port: 5432
```
The `-p` pipe makes Docker Postgres look like a local install.

### Option 3 — VS Code SQLTools extension
Install SQLTools + Postgres driver in VS Code. Browse tables directly inside the editor. No separate app needed.

### Summary
```
Local pgAdmin      →  -p pipe  →  Postgres in Docker
pgAdmin in Docker  →  Docker network by service name  →  Postgres in Docker
VS Code SQLTools   →  -p pipe  →  Postgres in Docker
```

---

## Quick Reference — Commands

```bash
# Start Redis in Docker
docker run -d --name redis-shopmate -p 6379:6379 redis:7-alpine

# Start Postgres in Docker
docker run -d --name pg -p 5432:5432 -e POSTGRES_PASSWORD=secret postgres:16

# Start pgAdmin in Docker
docker run -d --name pgadmin -p 5050:80 \
  -e PGADMIN_DEFAULT_EMAIL=admin@admin.com \
  -e PGADMIN_DEFAULT_PASSWORD=admin \
  dpage/pgadmin4

# See running containers
docker ps

# Stop a container
docker stop <container-name>

# Start a stopped container
docker start <container-name>

# Generate a secure JWT secret
python -c "import secrets; print(secrets.token_hex(32))"
```
