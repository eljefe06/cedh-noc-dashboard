from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, Field

Status      = Literal["ok", "warning", "critical", "down", "unknown"]
Criticality = Literal["high", "medium", "low"]


class Uptime(BaseModel):
    since: str
    seconds: int
    human: str


class Specs(BaseModel):
    vcpu: int
    ram_gb: int
    disk_gb: int


class Metrics(BaseModel):
    cpu_percent: float = Field(ge=0, le=100)
    ram_percent: float = Field(ge=0, le=100)
    disk_percent: float = Field(ge=0, le=100)
    load_1m: float = Field(ge=0)
    load_5m: float = Field(ge=0)
    load_15m: float = Field(ge=0)
    uptime_seconds: int = Field(ge=0)
    net_rx_mbps: float = Field(ge=0)
    net_tx_mbps: float = Field(ge=0)


class Service(BaseModel):
    name: str
    type: Literal["http", "tcp", "smtp", "imap", "process", "queue"]
    criticality: Criticality
    status: Status
    http_status: int | None
    latency_ms: int | None
    p95_ms_24h: int | None
    last_checked: str
    last_error: str | None
    url_checked: str | None
    extra: dict[str, Any] = {}


class SslCert(BaseModel):
    domain: str
    days_left: int
    expires_at: str
    issuer: str
    status: Status
    checked_externally: bool
    last_checked: str


class Backup(BaseModel):
    name: str
    last_backup_at: str
    last_backup_age_hours: float
    last_backup_size_mb: float
    last_backup_path: str
    status: Status


class Deploy(BaseModel):
    repo: str
    branch: str
    commit_sha: str
    commit_message: str
    author: str
    deployed_at: str
    age_hours: float
    status: Status


class DockerContainer(BaseModel):
    name: str
    image: str
    status: Literal["running", "exited", "paused", "restarting", "dead", "created"]
    health: Literal["healthy", "unhealthy", "starting", "none"]
    cpu_percent: float
    memory_mb: float
    memory_limit_mb: float
    restarts: int
    uptime_seconds: int
    ports: list[str]
    compose_project: str | None


class DockerInfo(BaseModel):
    available: bool
    engine_version: str
    containers_total: int
    containers_running: int
    containers_unhealthy: int
    containers_exited: int
    containers: list[DockerContainer]


class Server(BaseModel):
    name: str
    display_name: str
    status: Status
    provider: str
    region: str
    specs: Specs
    tailscale_ip: str | None
    agent_reachable: bool
    agent_last_seen: str
    stale: bool
    metrics: Metrics
    services: list[Service]
    ssl: list[SslCert]
    backups: list[Backup]
    deploys: list[Deploy]
    docker: DockerInfo | None


class DnsCheck(BaseModel):
    domain: str
    check_type: Literal["mx", "spf", "dmarc", "dkim", "a", "aaaa", "ptr", "smtp_starttls", "imap_tls"]
    expected: str
    actual: str
    status: Status
    resolver: str
    criticality: Criticality
    last_checked: str


class Incident(BaseModel):
    id: str
    started_at: str
    resolved_at: str | None
    status: Literal["open", "acknowledged", "resolved"]
    severity: Literal["high", "medium", "low"]
    target_type: Literal["service", "server", "agent", "dns"]
    target_name: str
    summary: str
    first_error: str | None


class StatusResponse(BaseModel):
    generated_at: str
    schema_version: Literal["1.0"] = "1.0"
    overall_status: Status
    incidents_open: int
    uptime: Uptime
    servers: list[Server]
    dns_checks: list[DnsCheck]
    recent_incidents: list[Incident]
