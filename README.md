# URL Shortener API

Quantumica technical screening submission — a JSON REST API for URL shortening built with **FastAPI**, **PostgreSQL**, and **uv**, using a layered architecture.

## Architecture

```
app/
├── api/            # HTTP layer (routes, dependencies)
├── core/           # Config, database, rate limiting, exceptions
├── models/         # SQLAlchemy ORM models
├── repositories/   # Data access layer
├── schemas/        # Pydantic request/response models
└── services/       # Business logic
```

Request flow: **Route → Service → Repository → Database**

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- Or locally: Python 3.12+, [uv](https://docs.astral.sh/uv/), PostgreSQL 16

## Quick start (Docker)

```bash
docker compose up --build
```

The API listens on **http://localhost:8080**.

Interactive docs: **http://localhost:8080/docs**

## Local development

```bash
# Start PostgreSQL (or use docker compose up db -d)
cp .env.example .env

uv sync --all-groups
uv run uvicorn app.main:app --reload --port 8080
```

Create a test database for pytest:

```bash
docker compose up db -d
docker compose exec db psql -U postgres -c "CREATE DATABASE urlshortener_test;"
uv run pytest -v
```

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/links` | Create a short link |
| `GET` | `/api/links` | List all links (click count + created_at) |
| `DELETE` | `/api/links/{slug}` | Delete a link |
| `GET` | `/{slug}` | Redirect to target URL (302) |
| `GET` | `/health` | Service and database health *(bonus)* |

## curl examples

**Create a link (auto-generated slug):**

```bash
curl -s -X POST http://localhost:8080/api/links \
  -H "Content-Type: application/json" \
  -d '{"target_url": "https://www.python.org"}' | jq
```

**Create a link with custom slug and expiry:**

```bash
curl -s -X POST http://localhost:8080/api/links \
  -H "Content-Type: application/json" \
  -d '{
    "target_url": "https://fastapi.tiangolo.com",
    "slug": "fastapi",
    "expires_at": "2027-01-01T00:00:00+00:00"
  }' | jq
```

**List all links:**

```bash
curl -s http://localhost:8080/api/links | jq
```

**Follow a redirect:**

```bash
curl -i http://localhost:8080/fastapi
```

**Delete a link:**

```bash
curl -s -X DELETE http://localhost:8080/api/links/fastapi -w "\nHTTP %{http_code}\n"
```

**Health check:**

```bash
curl -s http://localhost:8080/health | jq
```

**Validation error (400):**

```bash
curl -s -X POST http://localhost:8080/api/links \
  -H "Content-Type: application/json" \
  -d '{"target_url": "not-a-url"}' | jq
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@localhost:5432/urlshortener` | Async PostgreSQL connection string |
| `RATE_LIMIT_REQUESTS` | `10` | Max POST requests per IP per window |
| `RATE_LIMIT_WINDOW_SECONDS` | `60` | Rate limit window in seconds |

## Known limitations

- **Rate limiting** is in-memory and per-process; it resets on restart and does not work across multiple replicas without a shared store (e.g. Redis).
- **Slug namespace** is global; there is no multi-tenant isolation.
- **Click analytics** are stored in the database but not exposed via a dedicated API endpoint (only click count is returned in list).
- **Reserved slugs** (`health`, `docs`, `api`, etc.) cannot be used as short links to avoid conflicting with system routes.
- **No authentication** — any client can create, list, or delete links.

## AI usage

See [AI_LOG.md](./AI_LOG.md) for a record of AI-assisted development during this project.
