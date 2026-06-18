# AI Usage Log

Mandatory log of significant AI interactions during this project.

| Tool used | What you asked / generated | What you changed / decided yourself |
|-----------|----------------------------|-------------------------------------|
| **Cursor (Claude)** | Scaffold the full URL shortener project: FastAPI layered architecture, PostgreSQL persistence, Docker, tests, and CI from the Quantumica brief. | Chose explicit layers (api → service → repository → models) rather than a flat structure. Added reserved-slug handling so `/{slug}` does not shadow `/health` or `/docs`. Used async SQLAlchemy + asyncpg for consistency with FastAPI's async stack. |
| **Cursor (Claude)** | Generate Pydantic validation schemas and a custom 400 handler for `RequestValidationError`. | Required timezone-aware `expires_at` and future-only expiry to avoid ambiguous local-time bugs. Kept error payloads structured (`field` + `message`) instead of raw Pydantic dumps. |
| **Cursor (Claude)** | Implement in-memory sliding-window rate limiting for `POST /api/links`. | Accepted the approach for the bonus requirement but documented the single-process limitation in README. Chose 429 responses with a clear message; kept limits configurable via env vars. |

## Reflection

AI was useful for boilerplate speed (project layout, Docker/CI wiring, test fixtures). The parts that needed human judgment were **architecture boundaries** (what belongs in service vs repository), **edge cases** (expired links, reserved slugs, duplicate slug races via DB constraints), and **operational honesty** in the README about rate-limit and analytics limitations. I reviewed all generated code for security basics (parameterised queries via ORM, URL validation via Pydantic `HttpUrl`, no raw SQL from user input) before accepting it.
