from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.models import (
    DnsCheck,
    Incident,
    Metrics,
    Server,
    Service,
    Specs,
    SslCert,
    StatusResponse,
    Uptime,
)


def test_status_response_valid(mock_status):
    resp = StatusResponse(**mock_status)
    assert resp.schema_version == "1.0"
    assert len(resp.servers) == 4
    assert resp.overall_status in ("ok", "warning", "critical", "down", "unknown")


def test_status_response_servers_have_metrics(mock_status):
    resp = StatusResponse(**mock_status)
    for srv in resp.servers:
        assert 0 <= srv.metrics.cpu_percent <= 100
        assert 0 <= srv.metrics.ram_percent <= 100
        assert 0 <= srv.metrics.disk_percent <= 100


def test_status_response_services_criticality(mock_status):
    resp = StatusResponse(**mock_status)
    for srv in resp.servers:
        for svc in srv.services:
            assert svc.criticality in ("high", "medium", "low")
            assert svc.status in ("ok", "warning", "critical", "down", "unknown")


def test_status_response_ssl_days_left(mock_status):
    resp = StatusResponse(**mock_status)
    mail = next(s for s in resp.servers if s.name == "vps-mail")
    ssl = mail.ssl[0]
    assert ssl.domain == "mail.cedhsinaloa.org.mx"
    assert ssl.days_left == 18
    assert ssl.status == "warning"


def test_service_rejects_bad_type():
    with pytest.raises(ValidationError):
        Service(
            name="test",
            type="ftp",  # not a valid type
            criticality="high",
            status="ok",
            http_status=None,
            latency_ms=None,
            p95_ms_24h=None,
            last_checked="2026-05-13T10:00:00-07:00",
            last_error=None,
            url_checked=None,
            extra={},
        )


def test_dns_check_valid(mock_status):
    resp = StatusResponse(**mock_status)
    assert len(resp.dns_checks) > 0
    for check in resp.dns_checks:
        assert check.check_type in (
            "mx", "spf", "dmarc", "dkim", "a", "aaaa", "ptr", "smtp_starttls", "imap_tls"
        )


def test_incident_open_status():
    inc = Incident(
        id="test-001",
        started_at="2026-05-13T10:00:00+00:00",
        resolved_at=None,
        status="open",
        severity="high",
        target_type="service",
        target_name="cedhsinaloa.org.mx",
        summary="HTTP 503 from cedhsinaloa.org.mx",
        first_error="Connection refused",
    )
    assert inc.status == "open"
    assert inc.resolved_at is None


def test_metrics_negative_values_rejected():
    with pytest.raises(ValidationError):
        Metrics(
            cpu_percent=-1,  # invalid
            ram_percent=50,
            disk_percent=50,
            load_1m=0.5,
            load_5m=0.5,
            load_15m=0.5,
            uptime_seconds=3600,
            net_rx_mbps=1.0,
            net_tx_mbps=1.0,
        )


def test_server_agent_unreachable():
    srv = Server(
        name="test-vps",
        display_name="Test VPS",
        status="down",
        provider="Hetzner",
        region="nbg1",
        specs=Specs(vcpu=2, ram_gb=4, disk_gb=80),
        tailscale_ip=None,
        agent_reachable=False,
        agent_last_seen="2026-05-13T09:00:00+00:00",
        stale=True,
        metrics=Metrics(
            cpu_percent=0, ram_percent=0, disk_percent=0,
            load_1m=0, load_5m=0, load_15m=0,
            uptime_seconds=0, net_rx_mbps=0, net_tx_mbps=0,
        ),
        services=[],
        ssl=[],
        backups=[],
        deploys=[],
        docker=None,
    )
    assert srv.agent_reachable is False
    assert srv.stale is True
