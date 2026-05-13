from __future__ import annotations

import asyncio
import logging
import re

import asyncssh

from app.collectors.base import DockerContainerResult, DockerResult

log = logging.getLogger("noc.collector.docker")

# Tab-delimited: Name, Image, State, Status, compose project label
_CMD = (
    "docker version --format '{{.Server.Version}}' 2>/dev/null || echo ''; "
    "echo '==='; "
    r"docker ps -a --no-trunc --format "
    r"'{{.Names}}" + "\t" + r"{{.Image}}" + "\t" + r"{{.State}}" + "\t" + r"{{.Status}}" + "\t"
    r"{{.Label \"com.docker.compose.project\"}}' 2>/dev/null"
)

_UPTIME_RE = re.compile(
    r"Up\s+(?:(\d+)\s+weeks?\s*)?(?:(\d+)\s+days?\s*)?(?:(\d+)\s+hours?\s*)?(?:(\d+)\s+minutes?\s*)?",
    re.IGNORECASE,
)


def _parse_uptime(status: str) -> int:
    """Convert 'Up 2 days, 3 hours' → seconds. Returns 0 if exited/unknown."""
    m = _UPTIME_RE.search(status)
    if not m:
        return 0
    weeks, days, hours, mins = (int(g or 0) for g in m.groups())
    return weeks * 604800 + days * 86400 + hours * 3600 + mins * 60


def _parse_health(status: str) -> str:
    s = status.lower()
    if "(healthy)" in s:
        return "healthy"
    if "(unhealthy)" in s:
        return "unhealthy"
    if "(starting)" in s:
        return "starting"
    return "none"


def _parse_output(output: str) -> DockerResult:
    lines = output.strip().splitlines()
    if not lines:
        return DockerResult(error="no output")

    sep = next((i for i, l in enumerate(lines) if l.strip() == "==="), None)
    if sep is None:
        return DockerResult(error="unexpected format")

    engine_version = lines[0].strip() if sep > 0 else ""
    container_lines = lines[sep + 1 :]

    containers: list[DockerContainerResult] = []
    for line in container_lines:
        parts = line.split("\t")
        if len(parts) < 4:
            continue
        name, image, state, status_str = parts[0], parts[1], parts[2], parts[3]
        compose_project = parts[4].strip() if len(parts) > 4 else None

        # Normalize state
        state = state.lower().strip()
        if state not in ("running", "exited", "paused", "restarting", "dead", "created"):
            state = "created"

        containers.append(
            DockerContainerResult(
                name=name.lstrip("/"),
                image=image.split("@sha256:")[0],  # strip digest
                status=state,
                health=_parse_health(status_str),
                uptime_seconds=_parse_uptime(status_str),
                compose_project=compose_project or None,
            )
        )

    running = sum(1 for c in containers if c.status == "running")
    unhealthy = sum(1 for c in containers if c.health == "unhealthy")
    exited = sum(1 for c in containers if c.status == "exited")

    return DockerResult(
        available=True,
        engine_version=engine_version,
        containers=containers,
    )


async def collect_docker(
    host: str,
    username: str = "root",
    *,
    key_path: str = "/root/.ssh/noc_collector_ed25519",
    timeout: float = 20.0,
) -> DockerResult:
    try:
        async with asyncssh.connect(
            host,
            username=username,
            client_keys=[key_path],
            known_hosts=None,
            connect_timeout=timeout,
        ) as conn:
            result = await asyncio.wait_for(conn.run(_CMD), timeout=timeout)
        if not result.stdout:
            return DockerResult(error="empty output")
        return _parse_output(result.stdout)
    except asyncssh.DisconnectError as exc:
        return DockerResult(error=f"ssh disconnect: {exc.reason[:60]}")
    except (asyncssh.ConnectionLost, asyncssh.PermissionDenied) as exc:
        return DockerResult(error=str(exc)[:80])
    except asyncio.TimeoutError:
        return DockerResult(error="timeout")
    except Exception as exc:
        log.warning("collect_docker %s@%s: %s", username, host, exc)
        return DockerResult(error=str(exc)[:80])
