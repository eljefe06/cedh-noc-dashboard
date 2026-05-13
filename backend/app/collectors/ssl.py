from __future__ import annotations

import asyncio
import logging
import socket
import ssl
from datetime import datetime, timezone

from cryptography import x509
from cryptography.hazmat.backends import default_backend

log = logging.getLogger("noc.collector.ssl")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _fetch_cert_blocking(domain: str, port: int, timeout: float) -> bytes | str:
    """Blocking TLS handshake to grab the DER cert. Returns bytes or error string."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        with socket.create_connection((domain, port), timeout=timeout) as sock:
            with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
                return ssock.getpeercert(binary_form=True)
    except Exception as exc:
        return str(exc)[:100]


async def check_ssl(domain: str, port: int = 443, *, timeout: float = 10.0) -> dict:
    """Check SSL certificate; returns a SslCert-compatible dict."""
    loop = asyncio.get_event_loop()
    try:
        raw = await asyncio.wait_for(
            loop.run_in_executor(None, _fetch_cert_blocking, domain, port, timeout),
            timeout=timeout + 3,
        )
    except asyncio.TimeoutError:
        return _error(domain, "timeout")

    if isinstance(raw, str):
        return _error(domain, raw)

    try:
        cert = x509.load_der_x509_certificate(raw, default_backend())
        expires_at: datetime = cert.not_valid_after_utc
        now = datetime.now(timezone.utc)
        days_left = (expires_at - now).days

        orgs = cert.issuer.get_attributes_for_oid(x509.NameOID.ORGANIZATION_NAME)
        issuer = orgs[0].value[:40] if orgs else "unknown"

        if days_left < 0:
            status = "down"
        elif days_left < 7:
            status = "critical"
        elif days_left < 30:
            status = "warning"
        else:
            status = "ok"

        return {
            "domain": domain,
            "days_left": days_left,
            "expires_at": expires_at.isoformat(),
            "issuer": issuer,
            "status": status,
            "checked_externally": True,
            "last_checked": _now(),
        }
    except Exception as exc:
        return _error(domain, f"parse error: {exc!s:.80}")


def _error(domain: str, msg: str) -> dict:
    return {
        "domain": domain,
        "days_left": -1,
        "expires_at": "",
        "issuer": "",
        "status": "down",
        "checked_externally": True,
        "last_checked": _now(),
        "error": msg,
    }
