from fastapi import APIRouter

from app.core.database import check_db_connection

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict:
    db_ok = await check_db_connection()
    status_value = "ok" if db_ok else "degraded"
    return {
        "status": status_value,
        "database": "connected" if db_ok else "disconnected",
    }
