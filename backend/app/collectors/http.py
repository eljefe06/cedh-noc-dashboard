from __future__ import annotations

import asyncio
import ssl
import time

import httpx

from app.collectors.base import CheckResult


def _latency_status(ms: int | None) -> str:
    """Slowness alone is at most a warning — availability decides critical/down.

    Thresholds calibrated for checks that traverse the public internet
    (Culiacán → Hetzner/Hostinger EU adds ~150-300ms baseline).
    """
    if ms is None:
        return "down"
    if ms < 1500:
        return "ok"
    return "warning"


def _http_status_to_check_status(code: int, ok_codes: set[int]) -> str:
    if code in ok_codes:
        return "ok"
    if code in (301, 302, 303, 307, 308):
        return "ok"
    if 400 <= code < 500:
        return "warning"
    return "critical"


async def check_http(
    url: str,
    *,
    timeout: float = 8.0,
    ok_codes: set[int] | None = None,
    follow_redirects: bool = False,
) -> CheckResult:
    if ok_codes is None:
        ok_codes = {200, 201, 301, 302, 304, 404}

    t0 = time.monotonic()
    try:
        async with httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=follow_redirects,
            verify=False,  # some internal services use self-signed certs
        ) as client:
            resp = await client.get(url)
        ms = int((time.monotonic() - t0) * 1000)
        base = _http_status_to_check_status(resp.status_code, ok_codes)
        lat = _latency_status(ms)
        # take the worse of the two
        order = ["ok", "warning", "critical", "down"]
        status = order[max(order.index(base), order.index(lat))]
        return CheckResult(
            status=status,
            latency_ms=ms,
            http_status=resp.status_code,
        )
    except httpx.TimeoutException:
        return CheckResult(status="down", error="timeout", latency_ms=int(timeout * 1000))
    except Exception as exc:
        return CheckResult(status="down", error=str(exc)[:120])


async def check_tcp(host: str, port: int, *, timeout: float = 8.0) -> CheckResult:
    """Plain TCP connect — used as pre-check for SMTP/IMAP."""
    t0 = time.monotonic()
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port), timeout=timeout
        )
        ms = int((time.monotonic() - t0) * 1000)
        banner = await asyncio.wait_for(reader.readline(), timeout=3.0)
        writer.close()
        await writer.wait_closed()
        return CheckResult(
            status=_latency_status(ms),
            latency_ms=ms,
            extra={"banner": banner.decode(errors="replace").strip()[:80]},
        )
    except asyncio.TimeoutError:
        return CheckResult(status="down", error="timeout")
    except Exception as exc:
        return CheckResult(status="down", error=str(exc)[:120])


async def check_smtp_starttls(host: str, port: int = 587, *, timeout: float = 8.0) -> CheckResult:
    """Connect to SMTP and verify STARTTLS is advertised."""
    t0 = time.monotonic()
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port), timeout=timeout
        )
        # Read greeting
        await asyncio.wait_for(reader.readline(), timeout=5.0)
        # Send EHLO
        writer.write(b"EHLO noc.check\r\n")
        await writer.drain()
        # Read EHLO response (multi-line)
        caps = b""
        while True:
            line = await asyncio.wait_for(reader.readline(), timeout=5.0)
            caps += line
            if line[3:4] == b" ":  # last line has space after code
                break
        writer.write(b"QUIT\r\n")
        await writer.drain()
        writer.close()
        await writer.wait_closed()

        ms = int((time.monotonic() - t0) * 1000)
        has_starttls = b"STARTTLS" in caps.upper()
        return CheckResult(
            status=_latency_status(ms),
            latency_ms=ms,
            extra={"starttls": has_starttls},
        )
    except asyncio.TimeoutError:
        return CheckResult(status="down", error="timeout")
    except Exception as exc:
        return CheckResult(status="down", error=str(exc)[:120])


async def check_imap_tls(host: str, port: int = 993, *, timeout: float = 8.0) -> CheckResult:
    """Connect to IMAP over TLS and verify greeting."""
    t0 = time.monotonic()
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port, ssl=ctx), timeout=timeout
        )
        greeting = await asyncio.wait_for(reader.readline(), timeout=5.0)
        writer.close()
        await writer.wait_closed()

        ms = int((time.monotonic() - t0) * 1000)
        ok = b"OK" in greeting.upper() or b"CAPABILITY" in greeting.upper()
        return CheckResult(
            status=_latency_status(ms) if ok else "critical",
            latency_ms=ms,
            extra={"tls": True, "greeting": greeting.decode(errors="replace").strip()[:60]},
        )
    except asyncio.TimeoutError:
        return CheckResult(status="down", error="timeout")
    except Exception as exc:
        return CheckResult(status="down", error=str(exc)[:120])
