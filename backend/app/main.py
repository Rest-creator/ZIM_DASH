"""ZIM DASH API entrypoint. Routers for orders, payments, and dispatch
arrive with their own tasks (ZD-M1-05, 04, 11)."""

from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.core.config import settings

app = FastAPI(title=settings.app_name)
app.include_router(auth_router)


@app.get("/health")
async def health() -> dict[str, str]:
    """Liveness/readiness probe. Deliberately dependency-free for now — once
    Postgres/Redis are wired in (ZD-M1-01), this should check both and
    report which one failed, not just that the process is alive."""
    return {"status": "ok", "environment": settings.environment}
