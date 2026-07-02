from __future__ import annotations

"""
Scheduler — runs all collectors on their poll intervals and writes
the aggregated StatusResponse to the SQLite cache every cycle.

State is kept in a plain dict in memory; the SQLite cache is only
written so that the API endpoint can serve it without locking on
the collector coroutines.
"""

import asyncio
import logging
import time
from datetime import datetime, timezone

from app.aggregator import build_status_response
from app.collectors.dns import check_dns
from app.collectors.docker_ssh import collect_docker
from app.collectors.http import check_http, check_imap_tls, check_smtp_starttls
from app.collectors.ssh_metrics import collect_metrics
from app.collectors.ssl import check_ssl
from app.config import Settings
from app.service_config import DNS_CHECKS, SERVERS, ServiceDef
from app.storage import (
    cache_set,
    incident_open,
    incident_resolve_by_target,
    incidents_open_list,
    incidents_recent,
)

log = logging.getLogger("noc.scheduler")

_TICK = 5  # main loop wakeup interval (seconds)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ─── Service check dispatch ───────────────────────────────────────────────────

async def _check_service(svc: ServiceDef, timeout: float) -> dict:
    """Run the right collector for a ServiceDef; return a Service-shaped dict."""
    base = {
        "name": svc.name,
        "type": svc.type,
        "criticality": svc.criticality,
        "http_status": None,
        "latency_ms": None,
        "p95_ms_24h": None,
        "last_error": None,
        "url_checked": svc.url,
        "extra": {},
    }

    if svc.type == "http":
        r = await check_http(
            svc.url,
            timeout=timeout,
            ok_codes=set(svc.ok_codes),
            follow_redirects=svc.follow_redirects,
        )
        base.update(
            {
                "status": r.status,
                "http_status": r.http_status,
                "latency_ms": r.latency_ms,
                "last_error": r.error,
                "last_checked": r.checked_at,
                "extra": r.extra,
            }
        )

    elif svc.type == "smtp":
        r = await check_smtp_starttls(svc.host, svc.port or 587, timeout=timeout)
        base.update(
            {
                "status": r.status,
                "latency_ms": r.latency_ms,
                "last_error": r.error,
                "last_checked": r.checked_at,
                "url_checked": f"{svc.host}:{svc.port}",
                "extra": r.extra,
            }
        )

    elif svc.type == "imap":
        r = await check_imap_tls(svc.host, svc.port or 993, timeout=timeout)
        base.update(
            {
                "status": r.status,
                "latency_ms": r.latency_ms,
                "last_error": r.error,
                "last_checked": r.checked_at,
                "url_checked": f"{svc.host}:{svc.port}",
                "extra": r.extra,
            }
        )

    else:
        base.update({"status": "unknown", "last_checked": _now()})

    return base


# ─── Per-server collector ─────────────────────────────────────────────────────

async def _collect_server(srv, state: dict, settings: Settings, do_metrics: bool) -> None:
    """Collect all data for one server and update state[srv.name].

    HTTP service checks run on every cycle; SSH metrics + Docker only
    when `do_metrics` is True (poll_interval_metrics elapsed) — otherwise
    the last collected values are kept.
    """
    name = srv.name
    prev = state.get(name, {})

    # --- HTTP service checks (fast, run every HTTP interval)
    service_tasks = [_check_service(svc, settings.http_timeout_seconds) for svc in srv.services]
    service_results = await asyncio.gather(*service_tasks, return_exceptions=True)
    services = []
    for svc_def, result in zip(srv.services, service_results):
        if isinstance(result, Exception):
            services.append(
                {
                    "name": svc_def.name,
                    "type": svc_def.type,
                    "criticality": svc_def.criticality,
                    "status": "unknown",
                    "http_status": None,
                    "latency_ms": None,
                    "p95_ms_24h": None,
                    "last_checked": _now(),
                    "last_error": str(result)[:80],
                    "url_checked": svc_def.url,
                    "extra": {},
                }
            )
        else:
            services.append(result)

    state.setdefault(name, {})["services"] = services

    # --- SSH metrics + Docker (only when the metrics interval elapsed)
    if not do_metrics:
        return

    metrics = await collect_metrics(
        srv.ssh_host,
        srv.ssh_user,
        key_path=settings.ssh_key_path,
        timeout=settings.ssh_timeout_seconds,
    )
    ssh_ok = metrics.error is None
    if ssh_ok:
        state[name]["metrics"] = metrics
        state[name]["agent_last_seen"] = _now()
    else:
        # keep last good metrics so the card doesn't zero out on a blip
        state[name].setdefault("metrics", metrics)
        state[name]["agent_last_seen"] = prev.get("agent_last_seen", "")
    state[name]["agent_reachable"] = ssh_ok
    state[name]["stale"] = not ssh_ok

    docker = await collect_docker(
        srv.ssh_host,
        srv.ssh_user,
        key_path=settings.ssh_key_path,
        timeout=settings.ssh_timeout_seconds,
    )
    if docker.available:
        state[name]["docker"] = docker
    else:
        # keep last good docker snapshot on a transient SSH failure
        state[name].setdefault("docker", None)

    log.debug(
        "server %s: agent=%s cpu=%.1f ram=%.1f services=%d",
        name,
        ssh_ok,
        metrics.cpu_percent,
        metrics.ram_percent,
        len(services),
    )


async def _collect_ssl(state: dict, settings: Settings) -> None:
    for srv in SERVERS:
        ssl_list = []
        tasks = [check_ssl(sd.domain, timeout=settings.http_timeout_seconds) for sd in srv.ssl_domains]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for sd, result in zip(srv.ssl_domains, results):
            if isinstance(result, Exception):
                ssl_list.append(
                    {
                        "domain": sd.domain,
                        "days_left": -1,
                        "expires_at": "",
                        "issuer": "",
                        "status": "down",
                        "checked_externally": True,
                        "last_checked": _now(),
                        "error": str(result)[:80],
                    }
                )
            else:
                ssl_list.append(result)
        state.setdefault(srv.name, {})["ssl"] = ssl_list


async def _collect_dns(state: dict, settings: Settings) -> None:
    tasks = [
        check_dns(
            chk.check_type,
            chk.domain,
            chk.expected,
            criticality=chk.criticality,
            resolvers=settings.dns_resolvers_list,
            timeout=settings.dns_timeout_seconds,
        )
        for chk in DNS_CHECKS
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    dns_checks = []
    for chk, result in zip(DNS_CHECKS, results):
        if isinstance(result, Exception):
            dns_checks.append(
                {
                    "domain": chk.domain,
                    "check_type": chk.check_type,
                    "expected": chk.expected,
                    "actual": "",
                    "status": "unknown",
                    "resolver": "1.1.1.1",
                    "criticality": chk.criticality,
                    "last_checked": _now(),
                }
            )
        else:
            dns_checks.append(result)
    state["__dns__"] = dns_checks


# ─── Incident management ──────────────────────────────────────────────────────

def _manage_incidents(state: dict, prev_services: dict, db) -> None:
    """
    Detect service status transitions and open/close incidents.
    prev_services: {server_name: {service_name: status}}
    """
    import uuid

    for srv in SERVERS:
        name = srv.name
        current_services = {s["name"]: s for s in state.get(name, {}).get("services", [])}
        prev = prev_services.get(name, {})

        for svc_name, svc in current_services.items():
            cur_status = svc.get("status", "unknown")
            old_status = prev.get(svc_name, "ok")
            target_name = f"{name}/{svc_name}"

            if cur_status in ("down", "critical") and old_status not in ("down", "critical"):
                severity = "high" if svc.get("criticality") == "high" else "medium"
                summary = f"{svc_name} on {name} is {cur_status}"
                first_error = svc.get("last_error") or svc.get("url_checked") or ""
                incident_open(
                    db,
                    id=str(uuid.uuid4()),
                    severity=severity,
                    target_type="service",
                    target_name=target_name,
                    summary=summary,
                    first_error=first_error,
                )
                log.warning("INCIDENT OPEN: %s", summary)

            elif cur_status == "ok" and old_status in ("down", "critical"):
                incident_resolve_by_target(db, "service", target_name)
                log.info("INCIDENT RESOLVED: %s", target_name)


# ─── Main scheduler loop ──────────────────────────────────────────────────────

async def run_scheduler(app_state, db, settings: Settings) -> None:
    """
    Background task started in lifespan. Runs indefinitely.
    app_state is the FastAPI app.state object (holds start_time).
    """
    state: dict = {}
    prev_services: dict = {}

    last_metrics = 0.0
    last_ssl = 0.0
    last_dns = 0.0

    log.info("Scheduler started — HTTP interval=%ds, metrics=%ds, SSL=%ds, DNS=%ds",
             settings.poll_interval_http, settings.poll_interval_metrics,
             settings.poll_interval_ssl, settings.poll_interval_dns)

    while True:
        now = time.monotonic()
        cycle_start = now

        # ── HTTP service checks (fastest interval) ────────────────────────
        # Run all servers concurrently. SSH metrics/Docker only piggyback
        # when their (slower) interval elapsed — SSHing every HTTP cycle
        # hammers the monitored VPS and multiplies transient failures.
        try:
            do_metrics = (now - last_metrics) >= settings.poll_interval_metrics
            do_ssl = (now - last_ssl) >= settings.poll_interval_ssl
            do_dns = (now - last_dns) >= settings.poll_interval_dns

            server_tasks = [_collect_server(srv, state, settings, do_metrics) for srv in SERVERS]
            await asyncio.gather(*server_tasks, return_exceptions=True)

            if do_metrics:
                last_metrics = now

            if do_ssl:
                await _collect_ssl(state, settings)
                last_ssl = now

            if do_dns:
                await _collect_dns(state, settings)
                last_dns = now

        except Exception as exc:
            log.error("Scheduler cycle error: %s", exc, exc_info=True)

        # ── Incident management ───────────────────────────────────────────
        try:
            _manage_incidents(state, prev_services, db)
            # Update snapshot for next cycle
            for srv in SERVERS:
                prev_services[srv.name] = {
                    s["name"]: s.get("status", "unknown")
                    for s in state.get(srv.name, {}).get("services", [])
                }
        except Exception as exc:
            log.error("Incident management error: %s", exc)

        # ── Build and cache status response ───────────────────────────────
        try:
            open_incidents = incidents_open_list(db)
            recent = incidents_recent(db, n=10)
            response = build_status_response(
                state,
                recent_incidents=recent,
                open_incident_count=len(open_incidents),
                api_start_time=app_state.start_time,
            )
            cache_set(db, "status", response)
            log.debug(
                "Status cached: overall=%s servers=%d open_incidents=%d cycle=%.1fs",
                response["overall_status"],
                len(response["servers"]),
                len(open_incidents),
                time.monotonic() - cycle_start,
            )
        except Exception as exc:
            log.error("Cache write error: %s", exc)

        # ── Sleep until next HTTP poll ────────────────────────────────────
        elapsed = time.monotonic() - cycle_start
        sleep_time = max(0.5, settings.poll_interval_http - elapsed)
        await asyncio.sleep(sleep_time)
