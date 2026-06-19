# AI Usage Log

Mandatory log of significant AI interactions during this project.

| Tool used | What you asked / generated | What you changed / decided yourself |
|-----------|----------------------------|-------------------------------------|
| **ChatGPT** | Help me plan the project structure before writing code — asked for a FastAPI layered layout and which folders belong in each layer. | Used the outline as a starting point but dropped the suggested `domain/` and `infrastructure/` split; felt like overkill for a week-long task. Went with a simpler `api / services / repositories / models / schemas / core` layout instead. |
| **Cursor (Claude)** | Scaffold the full URL shortener from the Quantumica brief: endpoints, PostgreSQL, Docker on 8080, uv. | Accepted most of the scaffold. Changed the redirect route to block reserved slugs (`health`, `docs`, `api`) — the first version would have let `GET /health` get swallowed by `/{slug}` depending on router order. Also switched from `uv run uvicorn` in the Dockerfile to calling `.venv/bin/uvicorn` directly after noticing dev deps were being installed on every container start. |
| **GitHub Copilot** | Inline suggestions while writing `link_repository.py` — `generate_unique_slug()` and the `IntegrityError` → `SlugAlreadyExistsError` mapping. | Accepted the slug generation loop (secrets + retry). Rejected Copilot's suggestion to use `random.randint` for slug IDs — wanted unpredictable slugs, not sequential numbers. Kept the DB unique constraint as the final guard against race conditions rather than relying on the pre-check alone. |
| **Cursor (Claude)** | Generate Pydantic schemas and a custom validation error handler (brief asks for 400, not 422). | Modified `expires_at` validation to require timezone info and reject past dates — AI's first version only checked the URL format. Rewrote the error handler output to return `{detail, errors[]}` with readable field names instead of FastAPI's default nested loc tuples. |
| **Cursor (Claude)** | Write pytest fixtures and integration tests against PostgreSQL. | Tests initially used 1–2 character slugs (`"a"`, `"go"`) which failed validation (min 3 chars) — caught that myself when pytest failed, not the AI. Added the `dependency_overrides` pattern for `get_db` so all requests in one test share the same session; AI's first fixture created a new session per request and list/redirect tests returned empty results. |


## Reflection

AI handled the parts I would have typed slowly anyway: boilerplate, Docker/CI wiring, test scaffolding, and docs. The bits I had to think through myself were where AI tends to slip — **router ordering and reserved paths**, **timezone handling on expiry**, **test isolation with async sessions**, and **being honest about limitations** (rate limiter is per-process, click analytics aren't exposed via API yet). I didn't copy anything blindly; I ran the test suite and a manual curl walkthrough after each major chunk and fixed what broke. The layered architecture wasn't AI's idea — I wanted the repo to read like something I'd maintain on a real team, not a single 300-line `main.py`.
