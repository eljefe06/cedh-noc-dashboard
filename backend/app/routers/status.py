from __future__ import annotations

import time
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings
from app.models import StatusResponse
from app.storage import cache_get, incidents_open_count, incidents_recent

router = APIRouter(prefix="/api/v1")
_bearer = HTTPBearer(auto_error=False)

# Uptime tracking — module-level so it survives across requests
_start_time = time.time()


def _verify_token(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> None:
    """Require Bearer token only if one is configured (not the default 'changeme')."""
    if settings.noc_api_bearer_token == "changeme":
        return  # dev mode — no auth
    if creds is None or creds.credentials != settings.noc_api_bearer_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing Bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/health")
async def health() -> dict:
    uptime_sec = int(time.time() - _start_time)
    return {
        "status": "ok",
        "uptime_seconds": uptime_sec,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/status", response_model=StatusResponse)
async def get_status(
    request: Request,
    _: None = Depends(_verify_token),
) -> StatusResponse:
    db = request.app.state.db

    cached = cache_get(db, "status")
    if cached:
        return StatusResponse(**cached)

    # No cache yet — return stale-safe empty skeleton so the frontend
    # always gets a valid response.  Phase 4 will populate real data.
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Collectors not yet initialized — no cached status available",
    )


@router.get("/incidents/recent")
async def incidents_recent_endpoint(
    request: Request,
    n: int = 20,
    _: None = Depends(_verify_token),
) -> list[dict]:
    db = request.app.state.db
    return incidents_recent(db, n)


@router.get("/incidents/open")
async def incidents_open_endpoint(
    request: Request,
    _: None = Depends(_verify_token),
) -> list[dict]:
    from app.storage import incidents_open_list
    db = request.app.state.db
    return incidents_open_list(db)


@router.get("/dns")
async def dns_endpoint(
    request: Request,
    _: None = Depends(_verify_token),
) -> list[dict]:
    db = request.app.state.db
    cached = cache_get(db, "status")
    if cached:
        return cached.get("dns_checks", [])
    return []
