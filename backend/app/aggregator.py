from __future__ import annotations

import logging
import time
from datetime import datetime, timezone

from app.collectors.base import DockerResult, MetricsResult
from app.service_config import SERVERS, ServerDef

log = logging.getLogger("noc.aggregator")

# Status severity order for comparisons
_ORD = {"ok": 0, "unknown": 1, "warning": 2, "critical": 3, "down": 4}


def _worse(a: str, b: str) -> str:
    return a if _ORD.get(a, 0) >= _ORD.get(b, 0) else b


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _metrics_status(cpu: float, ram: float, disk: float) -> str:
    """Convert resource percentages into a single status."""
    worst = "ok"
    for val in (cpu, ram, disk):
        if val > 90:
            worst = _worse(worst, "critical")
        elif val > 75:
            worst = _worse(worst, "warning")
    return worst


def server_status(agent_reachable: bool, services: list[dict], metrics: dict) -> str:
    """Apply API_CONTRACT server.status rules."""
    if not agent_reachable:
        return "down"

    # Rules 2+3: any high service down/critical → critical
    for svc in services:
        if svc.get("criticality") == "high" and svc.get("status") in ("down", "critical"):
            return "critical"

    # Rule 3 (metrics): any resource metric critical
    m_status = _metrics_status(
        metrics.get("cpu_percent", 0),
        metrics.get("ram_percent", 0),
        metrics.get("disk_percent", 0),
    )
    if m_status == "critical":
        return "critical"

    # Rule 4: any high service warning OR metrics warning
    for svc in services:
        if svc.get("criticality") == "high" and svc.get("status") == "warning":
            return "warning"
    if m_status == "warning":
        return "warning"

    return "ok"


def overall_status(servers: list[dict]) -> str:
    """Apply API_CONTRACT overall_status rules."""
    all_services = [svc for srv in servers for svc in srv.get("services", [])]

    # Rules 1+2: any high service down or critical → critical
    for svc in all_services:
        if svc.get("criticality") == "high" and svc.get("status") in ("down", "critical"):
            return "critical"

    # Rule 3: any high service warning → warning
    for svc in all_services:
        if svc.get("criticality") == "high" and svc.get("status") == "warning":
            return "warning"

    # Rule 4: any server critical → warning
    for srv in servers:
        if srv.get("status") == "critical":
            return "warning"

    # Rule 5: any medium service down/critical → warning
    for svc in all_services:
        if svc.get("criticality") == "medium" and svc.get("status") in ("down", "critical"):
            return "warning"

    # Rule 6: low never affects overall
    return "ok"


def _docker_to_dict(docker: DockerResult | None) -> dict | None:
    if docker is None or not docker.available:
        return None
    conts = []
    for c in docker.containers:
        conts.append(
            {
                "name": c.name,
                "image": c.image,
                "status": c.status,
                "health": c.health,
                "cpu_percent": c.cpu_percent,
                "memory_mb": c.memory_mb,
                "memory_limit_mb": c.memory_limit_mb,
                "restarts": c.restarts,
                "uptime_seconds": c.uptime_seconds,
                "ports": c.ports,
                "compose_project": c.compose_project,
            }
        )
    running = sum(1 for c in docker.containers if c.status == "running")
    unhealthy = sum(1 for c in docker.containers if c.health == "unhealthy")
    exited = sum(1 for c in docker.containers if c.status == "exited")
    return {
        "available": True,
        "engine_version": docker.engine_version,
        "containers_total": len(docker.containers),
        "containers_running": running,
        "containers_unhealthy": unhealthy,
        "containers_exited": exited,
        "containers": conts,
    }


def _metrics_to_dict(m: MetricsResult) -> dict:
    return {
        "cpu_percent": m.cpu_percent,
        "ram_percent": m.ram_percent,
        "disk_percent": m.disk_percent,
        "load_1m": m.load_1m,
        "load_5m": m.load_5m,
        "load_15m": m.load_15m,
        "uptime_seconds": m.uptime_seconds,
        "net_rx_mbps": m.net_rx_mbps,
        "net_tx_mbps": m.net_tx_mbps,
    }


def build_status_response(
    collected: dict,  # keyed by server name
    recent_incidents: list[dict],
    open_incident_count: int,
    api_start_time: float,
) -> dict:
    """
    Assemble the full StatusResponse from the collector state dict.

    `collected[server_name]` structure:
      {
        "agent_reachable": bool,
        "agent_last_seen": str,
        "stale": bool,
        "metrics": MetricsResult,
        "services": list[dict],   # already shaped like Service
        "ssl": list[dict],        # already shaped like SslCert
        "docker": DockerResult | None,
      }
    """
    now = time.time()
    uptime_secs = int(now - api_start_time)

    servers_out = []
    for srv_def in SERVERS:
        name = srv_def.name
        data = collected.get(name, {})

        agent_reachable = data.get("agent_reachable", False)
        agent_last_seen = data.get("agent_last_seen", "")
        stale = data.get("stale", True)
        metrics = data.get("metrics", MetricsResult(error="no data"))
        services = data.get("services", [])
        ssl_list = data.get("ssl", [])
        docker = data.get("docker", None)

        metrics_dict = _metrics_to_dict(metrics)
        srv_status = server_status(agent_reachable, services, metrics_dict)

        servers_out.append(
            {
                "name": name,
                "display_name": srv_def.display_name,
                "status": srv_status,
                "provider": srv_def.provider,
                "region": srv_def.region,
                "specs": srv_def.specs,
                "tailscale_ip": srv_def.tailscale_ip,
                "agent_reachable": agent_reachable,
                "agent_last_seen": agent_last_seen,
                "stale": stale,
                "metrics": metrics_dict,
                "services": services,
                "ssl": ssl_list,
                "backups": [],
                "deploys": [],
                "docker": _docker_to_dict(docker),
            }
        )

    dns_checks = collected.get("__dns__", [])
    o_status = overall_status(servers_out)

    uptime_h = uptime_secs // 3600
    uptime_d = uptime_h // 24
    uptime_hh = uptime_h % 24
    uptime_mm = (uptime_secs % 3600) // 60
    if uptime_d:
        uptime_human = f"{uptime_d}d {uptime_hh:02d}:{uptime_mm:02d}"
    else:
        uptime_human = f"{uptime_hh:02d}:{uptime_mm:02d}"

    return {
        "generated_at": _now(),
        "schema_version": "1.0",
        "overall_status": o_status,
        "incidents_open": open_incident_count,
        "uptime": {
            "since": datetime.fromtimestamp(api_start_time, tz=timezone.utc).isoformat(),
            "seconds": uptime_secs,
            "human": uptime_human,
        },
        "servers": servers_out,
        "dns_checks": dns_checks,
        "recent_incidents": recent_incidents,
    }
