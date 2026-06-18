from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.routes import health, links, redirect
from app.core.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="URL Shortener API",
    description="Quantumica technical screening — JSON REST API for URL shortening.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(health.router)
app.include_router(links.router)
app.include_router(redirect.router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    errors = []
    for error in exc.errors():
        loc = " -> ".join(str(part) for part in error.get("loc", []))
        errors.append({"field": loc, "message": error.get("msg", "Invalid value")})
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Validation failed", "errors": errors},
    )
