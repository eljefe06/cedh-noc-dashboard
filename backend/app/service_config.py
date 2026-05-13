from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

ServiceType = Literal["http", "tcp", "smtp", "imap", "process", "queue"]
Criticality = Literal["high", "medium", "low"]


@dataclass
class ServiceDef:
    name: str
    type: ServiceType
    criticality: Criticality
    url: str | None = None
    host: str | None = None
    port: int | None = None
    ok_codes: frozenset[int] = frozenset({200, 201, 301, 302, 304})
    follow_redirects: bool = False


@dataclass
class SslDomainDef:
    domain: str


@dataclass
class DnsCheckDef:
    check_type: str
    domain: str
    expected: str
    criticality: Criticality = "high"


@dataclass
class ServerDef:
    name: str
    display_name: str
    provider: str
    region: str
    specs: dict  # {vcpu, ram_gb, disk_gb}
    tailscale_ip: str | None
    ssh_host: str
    ssh_user: str
    services: list[ServiceDef] = field(default_factory=list)
    ssl_domains: list[SslDomainDef] = field(default_factory=list)


# ─── Server + service definitions from INVENTORY.md ──────────────────────────

SERVERS: list[ServerDef] = [
    ServerDef(
        name="vps-myrock",
        display_name="VPS MyRock",
        provider="Hetzner",
        region="nbg1",
        specs={"vcpu": 2, "ram_gb": 8, "disk_gb": 96},
        tailscale_ip="100.104.244.83",
        ssh_host="100.104.244.83",  # connect via Tailscale from inside the container
        ssh_user="root",
        services=[
            ServiceDef("MyRock", "http", "medium", url="https://myrock.com.mx/"),
            ServiceDef("PagoKids", "http", "high", url="https://pagokids.com.mx/"),
        ],
        ssl_domains=[
            SslDomainDef("myrock.com.mx"),
            SslDomainDef("pagokids.com.mx"),
        ],
    ),
    ServerDef(
        name="vps-suig",
        display_name="VPS SUIG",
        provider="Hetzner",
        region="fsn1",
        specs={"vcpu": 4, "ram_gb": 16, "disk_gb": 194},
        tailscale_ip=None,
        ssh_host="187.124.152.86",
        ssh_user="root",
        services=[
            ServiceDef(
                "cedhsinaloa.org.mx",
                "http",
                "high",
                url="https://cedhsinaloa.org.mx/",
                ok_codes=frozenset({200, 301, 302}),
            ),
            ServiceDef("SUIG", "http", "high", url="https://suig.cedhsinaloa.org.mx/"),
            # Root returns 404 (expected — app requires auth path)
            ServiceDef(
                "Buzon",
                "http",
                "high",
                url="https://buzon.cedhsinaloa.org.mx/",
                ok_codes=frozenset({404}),
            ),
            ServiceDef(
                "cedhs.xyz",
                "http",
                "medium",
                url="https://cedhs.xyz/",
                ok_codes=frozenset({200, 301, 302}),
            ),
        ],
        ssl_domains=[
            SslDomainDef("cedhsinaloa.org.mx"),
            SslDomainDef("suig.cedhsinaloa.org.mx"),
            SslDomainDef("buzon.cedhsinaloa.org.mx"),
        ],
    ),
    ServerDef(
        name="vps-oic",
        display_name="VPS OIC",
        provider="Hostinger",
        region="eu",
        specs={"vcpu": 2, "ram_gb": 8, "disk_gb": 97},
        tailscale_ip=None,
        ssh_host="31.220.58.97",
        ssh_user="root",
        services=[
            # HTTP → HTTPS redirect, follow it
            ServiceDef(
                "Declaraciones",
                "http",
                "high",
                url="https://declaraciones.cedhsinaloa.org.mx/",
                follow_redirects=True,
            ),
            ServiceDef("Portal OIC", "http", "high", url="https://oic.cedhsinaloa.org.mx/"),
            ServiceDef(
                "SIER",
                "http",
                "high",
                url="https://sier.cedhsinaloa.org.mx/",
                ok_codes=frozenset({200, 302}),
            ),
        ],
        ssl_domains=[
            SslDomainDef("oic.cedhsinaloa.org.mx"),
            SslDomainDef("sier.cedhsinaloa.org.mx"),
            # declaraciones has no SSL cert yet — check will return "down"
            SslDomainDef("declaraciones.cedhsinaloa.org.mx"),
        ],
    ),
    ServerDef(
        name="vps-mail",
        display_name="VPS Mail",
        provider="Local CEDH",
        region="culiacan",
        specs={"vcpu": 12, "ram_gb": 32, "disk_gb": 915},
        tailscale_ip="100.118.231.85",
        ssh_host="100.118.231.85",  # Tailscale — never public
        ssh_user="jyanagui",
        services=[
            # All mail services are checked via Tailscale (100.118.231.85), not public IP
            ServiceDef(
                "Mailcow SOGo",
                "http",
                "high",
                url="http://100.118.231.85/SOGo/",
                ok_codes=frozenset({200, 301, 302}),
            ),
            ServiceDef("SMTP", "smtp", "high", host="100.118.231.85", port=587),
            ServiceDef("IMAP", "imap", "high", host="100.118.231.85", port=993),
            ServiceDef(
                "Mailcow Admin",
                "http",
                "medium",
                url="http://100.118.231.85/",
                ok_codes=frozenset({200, 301, 302}),
            ),
        ],
        ssl_domains=[
            SslDomainDef("mail.cedhsinaloa.org.mx"),
        ],
    ),
]

# ─── DNS checks from INVENTORY.md ────────────────────────────────────────────

DNS_CHECKS: list[DnsCheckDef] = [
    DnsCheckDef("mx", "cedhsinaloa.org.mx", "mail.cedhsinaloa.org.mx", "high"),
    DnsCheckDef("spf", "cedhsinaloa.org.mx", "v=spf1", "high"),
    DnsCheckDef("dmarc", "_dmarc.cedhsinaloa.org.mx", "v=DMARC1", "high"),
    DnsCheckDef("a", "mail.cedhsinaloa.org.mx", "", "high"),
]

# Lookup by server name
SERVERS_BY_NAME: dict[str, ServerDef] = {s.name: s for s in SERVERS}
