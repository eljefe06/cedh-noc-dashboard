from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

import dns.exception
import dns.rdatatype
import dns.resolver
import dns.reversename

log = logging.getLogger("noc.collector.dns")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _resolver(servers: list[str]) -> dns.resolver.Resolver:
    r = dns.resolver.Resolver(configure=False)
    r.nameservers = servers or ["1.1.1.1", "8.8.8.8"]
    r.timeout = 5.0
    r.lifetime = 8.0
    return r


def _check_blocking(check_type: str, domain: str, expected: str, servers: list[str]) -> dict:
    r = _resolver(servers)
    try:
        if check_type == "mx":
            answers = r.resolve(domain, "MX")
            actual = " ".join(
                str(a.exchange).rstrip(".") for a in sorted(answers, key=lambda x: x.preference)
            )
            ok = any(expected.lower() in str(a.exchange).lower() for a in answers)
            return {"actual": actual, "status": "ok" if ok else "critical"}

        elif check_type in ("spf", "dmarc"):
            answers = r.resolve(domain, "TXT")
            records = [b"".join(a.strings).decode(errors="replace") for a in answers]
            match = [rec for rec in records if expected.lower() in rec.lower()]
            actual = match[0] if match else (records[0] if records else "")
            return {"actual": actual[:200], "status": "ok" if match else "critical"}

        elif check_type == "a":
            answers = r.resolve(domain, "A")
            actual = ", ".join(str(a) for a in answers)
            ok = (any(str(a) == expected for a in answers) if expected else bool(answers))
            return {"actual": actual, "status": "ok" if ok else "warning"}

        elif check_type == "ptr":
            rev = dns.reversename.from_address(domain)
            answers = r.resolve(rev, "PTR")
            actual = " ".join(str(a).rstrip(".") for a in answers)
            ok = any(expected.lower() in str(a).lower() for a in answers)
            return {"actual": actual, "status": "ok" if ok else "warning"}

        else:
            return {"actual": "", "status": "unknown"}

    except dns.resolver.NXDOMAIN:
        return {"actual": "NXDOMAIN", "status": "critical"}
    except dns.resolver.NoAnswer:
        return {"actual": "no answer", "status": "critical"}
    except dns.exception.Timeout:
        return {"actual": "timeout", "status": "down"}
    except Exception as exc:
        return {"actual": str(exc)[:60], "status": "unknown"}


async def check_dns(
    check_type: str,
    domain: str,
    expected: str,
    *,
    criticality: str = "high",
    resolvers: list[str] | None = None,
    timeout: float = 10.0,
) -> dict:
    """Run one DNS check; returns a DnsCheck-compatible dict."""
    servers = resolvers or ["1.1.1.1", "8.8.8.8"]
    loop = asyncio.get_event_loop()
    try:
        result = await asyncio.wait_for(
            loop.run_in_executor(None, _check_blocking, check_type, domain, expected, servers),
            timeout=timeout,
        )
    except asyncio.TimeoutError:
        result = {"actual": "timeout", "status": "down"}

    return {
        "domain": domain,
        "check_type": check_type,
        "expected": expected,
        "actual": result.get("actual", ""),
        "status": result.get("status", "unknown"),
        "resolver": servers[0],
        "criticality": criticality,
        "last_checked": _now(),
    }
