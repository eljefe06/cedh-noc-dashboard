from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class CheckResult:
    status: str          # ok | warning | critical | down | unknown
    latency_ms: int | None = None
    http_status: int | None = None
    error: str | None = None
    checked_at: str = field(default_factory=_now)
    extra: dict = field(default_factory=dict)


@dataclass
class MetricsResult:
    cpu_percent: float = 0.0
    ram_percent: float = 0.0
    disk_percent: float = 0.0
    load_1m: float = 0.0
    load_5m: float = 0.0
    load_15m: float = 0.0
    uptime_seconds: int = 0
    net_rx_mbps: float = 0.0
    net_tx_mbps: float = 0.0
    error: str | None = None
    checked_at: str = field(default_factory=_now)


@dataclass
class DockerContainerResult:
    name: str
    image: str
    status: str   # running | exited | paused | restarting | dead | created
    health: str   # healthy | unhealthy | starting | none
    restarts: int = 0
    uptime_seconds: int = 0
    ports: list[str] = field(default_factory=list)
    compose_project: str | None = None
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    memory_limit_mb: float = 0.0


@dataclass
class DockerResult:
    available: bool = False
    engine_version: str = ""
    containers: list[DockerContainerResult] = field(default_factory=list)
    error: str | None = None
    checked_at: str = field(default_factory=_now)
