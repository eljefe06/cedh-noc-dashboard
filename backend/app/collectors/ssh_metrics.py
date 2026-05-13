from __future__ import annotations

import asyncio
import logging

import asyncssh

from app.collectors.base import MetricsResult

log = logging.getLogger("noc.collector.ssh_metrics")

# One python3 one-liner that collects all metrics in ~1.5s.
# Samples CPU and net twice (1s apart) to compute rates.
_CMD = r"""python3 -c "
import time,re,os
def rd(f):return open(f).read()
def cpu():
    l=rd('/proc/stat').split('\n')[0].split()
    v=list(map(int,l[1:8]));return sum(v)-v[3],sum(v)
def net():
    rx=tx=0
    for l in rd('/proc/net/dev').split('\n'):
        if ':' not in l or 'lo:' in l:continue
        p=l.split(':')[1].split();rx+=int(p[0]);tx+=int(p[8])
    return rx,tx
ci,ct=cpu();nr1,nt1=net()
time.sleep(1)
ci2,ct2=cpu();nr2,nt2=net()
cpu_pct=round(100*(ci2-ci)/(ct2-ct),1) if ct2!=ct else 0
rx_mbps=round((nr2-nr1)*8/1e6,2);tx_mbps=round((nt2-nt1)*8/1e6,2)
m={k:int(v) for k,v in re.findall(r'(\w+):\s+(\d+)',rd('/proc/meminfo'))}
mt=m.get('MemTotal',1);ma=m.get('MemAvailable',0)
ram_pct=round(100*(mt-ma)/mt,1)
d=os.statvfs('/');disk_pct=round(100*(1-d.f_bfree/d.f_blocks),1) if d.f_blocks else 0
la=rd('/proc/loadavg').split()
up=int(float(rd('/proc/uptime').split()[0]))
print(f'{cpu_pct}|{ram_pct}|{disk_pct}|{la[0]}|{la[1]}|{la[2]}|{up}|{rx_mbps}|{tx_mbps}')
" 2>/dev/null
"""


def _parse(output: str) -> MetricsResult:
    parts = output.strip().split("|")
    if len(parts) != 9:
        return MetricsResult(error=f"bad output: {output.strip()[:60]}")
    try:
        return MetricsResult(
            cpu_percent=float(parts[0]),
            ram_percent=float(parts[1]),
            disk_percent=float(parts[2]),
            load_1m=float(parts[3]),
            load_5m=float(parts[4]),
            load_15m=float(parts[5]),
            uptime_seconds=int(parts[6]),
            net_rx_mbps=float(parts[7]),
            net_tx_mbps=float(parts[8]),
        )
    except (ValueError, IndexError) as exc:
        return MetricsResult(error=str(exc)[:80])


async def collect_metrics(
    host: str,
    username: str = "root",
    *,
    key_path: str = "/root/.ssh/noc_collector_ed25519",
    timeout: float = 20.0,
) -> MetricsResult:
    try:
        async with asyncssh.connect(
            host,
            username=username,
            client_keys=[key_path],
            known_hosts=None,  # V1 inside Tailscale — no host verification
            connect_timeout=timeout,
        ) as conn:
            result = await asyncio.wait_for(conn.run(_CMD), timeout=timeout)
        if not result.stdout and result.exit_status:
            return MetricsResult(error=f"exit {result.exit_status}")
        return _parse(result.stdout)
    except asyncssh.DisconnectError as exc:
        return MetricsResult(error=f"ssh disconnect: {exc.reason[:60]}")
    except (asyncssh.ConnectionLost, asyncssh.PermissionDenied) as exc:
        return MetricsResult(error=str(exc)[:80])
    except asyncio.TimeoutError:
        return MetricsResult(error="timeout")
    except Exception as exc:
        log.warning("collect_metrics %s@%s: %s", username, host, exc)
        return MetricsResult(error=str(exc)[:80])
