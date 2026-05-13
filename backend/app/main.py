from __future__ import annotations

import asyncio
import json
import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers.status import router as status_router
from app.scheduler import run_scheduler
from app.storage import cache_set, init_db

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
log = logging.getLogger("noc.main")

# Path to the bundled mock status — used to seed cache on first boot
# so /api/v1/status always works even before Phase 4 collectors run.
# In container: /app/app/main.py → .parent.parent = /app → /app/frontend/mock-data/status.json
_MOCK_FILE = Path(__file__).parent.parent / "frontend" / "mock-data" / "status.json"


# ── Lifespan ───────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Starting NOC API — initializing database at %s", settings.sqlite_db_path)
    db = init_db(settings.sqlite_db_path)
    app.state.db = db
    app.state.start_time = time.time()

    # Seed cache with mock data so the frontend works immediately (Phase 3).
    # Phase 4 collectors will overwrite this with real data.
    if _MOCK_FILE.exists():
        mock = json.loads(_MOCK_FILE.read_text())
        mock["generated_at"] = datetime.now(timezone.utc).isoformat()
        mock["_seeded_from_mock"] = True
        cache_set(db, "status", mock)
        log.info("Seeded status cache from mock-data/status.json")
    else:
        log.warning("Mock file not found at %s — /api/v1/status will return 503 until collectors run", _MOCK_FILE)

    # Start the collector scheduler as a background task
    scheduler_task = asyncio.create_task(
        run_scheduler(app.state, db, settings),
        name="noc-scheduler",
    )
    log.info("Scheduler started")

    yield

    log.info("Shutting down NOC API")
    scheduler_task.cancel()
    try:
        await scheduler_task
    except asyncio.CancelledError:
        pass
    db.close()


# ── App ────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="CEDH NOC API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["Authorization"],
)

app.include_router(status_router)


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.tailscale_ip,
        port=settings.api_port,
        log_level=settings.log_level.lower(),
        reload=False,
    )
