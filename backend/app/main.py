"""ZIM DASH API entrypoint (ZD-M1-02: boilerplate only — routers for auth,
orders, payments, dispatch and SSE arrive with their own tasks)."""

from fastapi import FastAPI

from app.core.config import settings

app = FastAPI(title=settings.app_name)


@app.get("/health")
async def health() -> dict[str, str]:
    """Liveness/readiness probe. Deliberately dependency-free for now — once
    Postgres/Redis are wired in (ZD-M1-01), this should check both and
    report which one failed, not just that the process is alive."""
    return {"status": "ok", "environment": settings.environment}
