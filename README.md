# URL Shortener – Backend Take-home

A **FastAPI** service that turns long URLs into short codes, tracks every redirect, and pushes live analytics over WebSockets. The project is fully containerised, covered by async tests, and designed for one-click deployment to **Google Cloud Run**.

---

## Table of contents

1. [Features](#features)
2. [Tech stack](#tech-stack)
3. [Local setup](#local-setup)
4. [API reference](#api-reference)
5. [Real-time analytics (WebSocket)](#real-time-analytics-websocket)
6. [Testing](#testing)
7. [Docker & Compose](#docker--compose)
8. [CI/CD pipeline](#cicd-pipeline)
9. [Cloud Run deployment](#cloud-run-deployment)
10. [Time break-down](#time-break-down)
11. [Trade-offs & future work](#trade-offs--future-work)

---

## Features

| Area                               | Details                                                                                            |
| ---------------------------------- | -------------------------------------------------------------------------------------------------- |
| **REST API**                       | `POST /shorten`, `GET /{code}`, `GET /analytics/{code}` – see below for example calls              |
| **Persistence**                    | Async SQLAlchemy + MySQL (default) with simple `create_all()` auto-migration                       |
| **Collision-safe code generation** | Up to 5 attempts to generate a unique 6-char slug                                                  |
| **Real-time analytics**            | WebSocket endpoint `/ws/analytics/{code}` broadcasts redirect counts to all subscribed clients     |
| **Observability ready**            | Structured JSON logs via Uvicorn; Cloud Logging picks them up automatically                        |
| **Container-first**                | One image runs anywhere (Docker, Compose, Cloud Run); health-checks wired in `docker-compose.yml`  |
| **CI quality gates**               | Black, Flake8, Pytest, and image build executed in GitHub Actions (see `.github/workflows/ci.yml`) |

---

## Tech stack

* **FastAPI 0.115** – high-performance async REST + WS
* **SQLAlchemy 1.4** (async) – ORM
* **MySQL 8** (via **aiomysql**) – default RDBMS
* **Pydantic v2** – schema validation&#x20;
* **Pytest + pytest-asyncio** – async integration tests&#x20;
* **Docker + docker-compose v3.9** – local orchestration&#x20;
* **GitHub Actions** – lint → test → build → push → deploy

---

## Local setup

### 1. Clone & create a virtual-env

```bash
git clone https://github.com/<your-name>/url-shortener.git
cd url-shortener
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt            # :contentReference[oaicite:7]{index=7}
```

### 2. Start MySQL and the API with Docker Compose

```bash
docker compose up -d --build
# API: http://localhost:8081
```

Compose exports two variables to the container:

* `ASYNC_DB_URL` – async SQLAlchemy DSN
* `BASE_URL` – external base URL used when we build the response to `/shorten`&#x20;

> **Note:** On startup FastAPI auto-creates the `short_urls` table if it is missing .

### 3. Running without Docker (optional)

```bash
export ASYNC_DB_URL='mysql+aiomysql://user:pass@127.0.0.1:3306/url_shortener'
export BASE_URL='http://localhost:8081'
uvicorn app.main:app --reload --port 8081
```

---

## API reference

### 1. Create a short link

```bash
curl -X POST http://localhost:8081/shorten \
     -H "Content-Type: application/json" \
     -d '{"url":"https://example.com"}'
```

<details>
<summary>Response 201</summary>

```json
{
  "short_code": "Ab3xYz",
  "short_url": "http://localhost:8081/Ab3xYz"
}
```

</details>

### 2. Redirect

```bash
curl -I http://localhost:8081/Ab3xYz
# HTTP/1.1 307 Temporary Redirect
# Location: https://example.com/
```

### 3. Fetch analytics

```bash
curl http://localhost:8081/analytics/Ab3xYz
```

Sample response (after one redirect):

```json
{
  "short_code":"Ab3xYz",
  "original_url":"https://example.com/",
  "created_at":"2025-05-22T03:45:12.345Z",
  "redirect_count":1
}
```

Analytics schema defined in `schemas.py` .

---

## Real-time analytics (WebSocket)

Open a WebSocket (e.g. with **wscat**):

```bash
wscat -c ws://localhost:8081/ws/analytics/Ab3xYz
```

* Upon connect you receive the current counter:

  ```json
  {"short_code":"Ab3xYz","redirect_count":1}
  ```
* Every new redirect triggers a broadcast to all live subscribers.
  Implementation in `websocket_manager.py` and `main.py` .

---

## Testing

```bash
pytest -q
```

`test_api.py` spins up an async client and WebSocket, verifying both the REST flow and live counter updates .

---

## Docker & Compose

### Build the image

```bash
docker build -t ghcr.io/<user>/url-shortener:latest .
```

(The `Dockerfile` stages: slim Python base → copy code → install deps → `uvicorn` entrypoint.)

### Multi-service compose

`docker-compose.yml` starts MySQL with a health-check and wires the backend to it .

---

## CI/CD pipeline

`.github/workflows/ci.yml` runs on every push:

1. **Lint**: `black --check` + `flake8`.
2. **Test**: `pytest` (including WebSocket integration).
3. **Build & push image**: tags `ghcr.io/<user>/url-shortener:$SHA`.
4. **Deploy** (optional): if branch = `main` it triggers `gcloud run deploy`.

---

## Cloud Run deployment

1. **Build & upload** (from root):

   ```bash
   gcloud builds submit --tag gcr.io/<project>/url-shortener
   ```
2. **Deploy**:

   ```bash
   gcloud run deploy url-shortener \
       --image gcr.io/<project>/url-shortener \
       --region us-central1 \
       --platform managed \
       --set-env-vars BASE_URL=https://<service-url>,ASYNC_DB_URL=${DB_URL} \
       --add-cloudsql-instances <project>:us-central1:url-shortener \
       --allow-unauthenticated
   ```
3. **IAM**:

   * Grant `Cloud SQL Client` to the Run service account.
   * Use Secret Manager for `DB_URL` if preferred.

---

## Time break-down

| Task              |     Hours |
| ----------------- | --------: |
| Core API & models |         2 |
| WebSocket layer   |         1 |
| Tests             |         1 |
| Docker & Compose  |       0.5 |
| CI pipeline       |       0.5 |
| README & cleanup  |       0.5 |
| **Total**         | **5.5 h** |

---

## Trade-offs & future work

* **No migrations**: rely on SQLAlchemy `create_all()` for brevity; Alembic can be added later.
* **In-memory cache**: redirect counts are fetched from DB each time; could push to Redis for lower latency.
* **Rate-limiting & auth**: not implemented; Cloud Armor or API Keys could be integrated.
* **Custom domains**: current `BASE_URL` env var allows one domain; mapping per-tenant is out-of-scope.
* **High-availability DB**: MySQL single instance in dev; Cloud SQL HA recommended in prod.

---

Happy shortening! 🎉
