# API_CONTRACT.md — Contrato JSON cerrado

> **Cerrado**. Si se cambia esto, se rompe la implementación. Cambios mayores requieren versionar: `/api/v1/` → `/api/v2/`.
> Versión schema: 1.0
> Última actualización: 2026-05-12

## Convenciones globales

- **Encoding**: UTF-8, JSON
- **Timestamps**: ISO 8601 con timezone, ejemplo: `2026-05-12T20:00:00-07:00`
- **Estados**: `"ok"` · `"warning"` · `"critical"` · `"down"` · `"unknown"`
- **Criticidad**: `"high"` · `"medium"` · `"low"`
- **Auth**: header `Authorization: Bearer <token>` (V1 puede ser opcional dentro de Tailscale)
- **Cache TTL API central**: 5 segundos
- **Códigos HTTP**:
  - `200` éxito
  - `401` token inválido
  - `503` collector backend no responde → la API devuelve último estado conocido con `"stale": true`

---

## Endpoint principal: `GET /api/v1/status`

Lo que la tablet consume cada 5 segundos.

### Schema

```typescript
interface StatusResponse {
  generated_at: string;           // ISO 8601 con TZ
  schema_version: "1.0";
  overall_status: Status;
  incidents_open: number;
  uptime: {
    since: string;                // ISO 8601
    seconds: number;
    human: string;                // ej. "14d 06:42"
  };
  servers: Server[];
  dns_checks: DnsCheck[];
  recent_incidents: Incident[];
}

type Status = "ok" | "warning" | "critical" | "down" | "unknown";
type Criticality = "high" | "medium" | "low";

interface Server {
  name: string;
  display_name: string;
  status: Status;
  provider: string;
  region: string;
  specs: { vcpu: number; ram_gb: number; disk_gb: number };
  tailscale_ip: string | null;
  agent_reachable: boolean;
  agent_last_seen: string;
  stale: boolean;
  metrics: {
    cpu_percent: number;
    ram_percent: number;
    disk_percent: number;
    load_1m: number;
    load_5m: number;
    load_15m: number;
    uptime_seconds: number;
    net_rx_mbps: number;
    net_tx_mbps: number;
  };
  services: Service[];
  ssl: SslCert[];
  backups: Backup[];
  deploys: Deploy[];
  docker: DockerInfo | null;       // V1.5
}

interface Service {
  name: string;
  type: "http" | "tcp" | "smtp" | "imap" | "process" | "queue";
  criticality: Criticality;
  status: Status;
  http_status: number | null;
  latency_ms: number | null;
  p95_ms_24h: number | null;
  last_checked: string;
  last_error: string | null;
  url_checked: string | null;
  extra: Record<string, any>;
}

interface SslCert {
  domain: string;
  days_left: number;
  expires_at: string;
  issuer: string;
  status: Status;
  checked_externally: boolean;
  last_checked: string;
}

interface Backup {
  name: string;
  last_backup_at: string;
  last_backup_age_hours: number;
  last_backup_size_mb: number;
  last_backup_path: string;
  status: Status;
}

interface Deploy {
  repo: string;
  branch: string;
  commit_sha: string;
  commit_message: string;
  author: string;
  deployed_at: string;
  age_hours: number;
  status: Status;
}

interface DnsCheck {
  domain: string;
  check_type: "mx" | "spf" | "dmarc" | "dkim" | "a" | "aaaa" | "ptr" | "smtp_starttls" | "imap_tls";
  expected: string;
  actual: string;
  status: Status;
  resolver: string;
  criticality: Criticality;
  last_checked: string;
}

interface Incident {
  id: string;
  started_at: string;
  resolved_at: string | null;
  status: "open" | "acknowledged" | "resolved";
  severity: "high" | "medium" | "low";
  target_type: "service" | "server" | "agent" | "dns";
  target_name: string;
  summary: string;
  first_error: string | null;
}

interface DockerInfo {
  available: boolean;
  engine_version: string;
  containers_total: number;
  containers_running: number;
  containers_unhealthy: number;
  containers_exited: number;
  containers: DockerContainer[];
}

interface DockerContainer {
  name: string;
  image: string;
  status: "running" | "exited" | "paused" | "restarting" | "dead" | "created";
  health: "healthy" | "unhealthy" | "starting" | "none";
  cpu_percent: number;
  memory_mb: number;
  memory_limit_mb: number;
  restarts: number;
  uptime_seconds: number;
  ports: string[];
  compose_project: string | null;
}
```

### Reglas de `overall_status`

Calculado en este orden:
1. Si **cualquier** servicio con `criticality: "high"` está `down` → `"critical"`
2. Si **cualquier** servicio con `criticality: "high"` está `critical` → `"critical"`
3. Si **cualquier** servicio con `criticality: "high"` está `warning` → `"warning"`
4. Si **cualquier** servidor está `critical` → `"warning"`
5. Si **cualquier** servicio `medium` está `down` o `critical` → `"warning"`
6. Servicios `low` **nunca** afectan `overall_status`
7. Default → `"ok"`

### Reglas de `server.status`

1. Si `agent_reachable: false` → `"down"`
2. Si cualquier servicio `high` en este server está `down` o `critical` → `"critical"`
3. Si cualquier métrica de recursos está `critical` → `"critical"`
4. Si cualquier servicio `high` está `warning` o métrica está `warning` → `"warning"`
5. Default → `"ok"`

---

## Endpoints adicionales V1

```
GET  /api/v1/status                  → JSON completo (este documento)
GET  /api/v1/server/{name}           → detalle de 1 servidor
GET  /api/v1/service/{server}/{name} → detalle de 1 servicio
GET  /api/v1/incidents/recent?n=20   → últimos N incidentes
GET  /api/v1/incidents/open          → solo incidentes abiertos
GET  /api/v1/dns                     → solo bloque DNS
GET  /api/v1/health                  → health de la API central misma
```

---

## Ejemplo de respuesta

```json
{
  "generated_at": "2026-05-12T20:00:00-07:00",
  "schema_version": "1.0",
  "overall_status": "warning",
  "incidents_open": 1,
  "uptime": {
    "since": "2026-04-28T13:18:00-07:00",
    "seconds": 1234567,
    "human": "14d 06:42"
  },
  "servers": [
    {
      "name": "vps-myrock",
      "display_name": "VPS MyRock",
      "status": "ok",
      "provider": "Hetzner",
      "region": "nbg1",
      "specs": {"vcpu": 2, "ram_gb": 8, "disk_gb": 96},
      "tailscale_ip": "100.x.x.x",
      "agent_reachable": true,
      "agent_last_seen": "2026-05-12T19:59:55-07:00",
      "stale": false,
      "metrics": {
        "cpu_percent": 12,
        "ram_percent": 36,
        "disk_percent": 56,
        "load_1m": 1.07,
        "load_5m": 1.20,
        "load_15m": 1.20,
        "uptime_seconds": 1234567,
        "net_rx_mbps": 2.1,
        "net_tx_mbps": 8.4
      },
      "services": [
        {"name": "MyRock", "type": "http", "criticality": "medium", "status": "ok", "http_status": 200, "latency_ms": 89, "p95_ms_24h": 142, "last_checked": "2026-05-12T19:59:55-07:00", "last_error": null, "url_checked": "https://myrock.com.mx/", "extra": {}}
      ],
      "ssl": [],
      "backups": [],
      "deploys": [],
      "docker": null
    }
  ],
  "dns_checks": [],
  "recent_incidents": []
}
```

---

## Manejo de fallas

Si la API central no puede contactar un servidor (SSH falla):
1. Marca `server.agent_reachable: false` y `server.stale: true`
2. Devuelve último estado conocido con timestamp claro
3. Genera incidente automático tras N=2 fallos consecutivos
4. Frontend muestra el servidor con indicador específico de "agente caído"

---

## Lo que NO está en este contrato (no implementar en V1)

- WebSocket de logs en vivo → V2
- Gráficas históricas 24h → V2
- Endpoints `POST /api/v1/action/*` → V3 con PIN+TOTP
- Heatmap 5xx por hora → V2
- DKIM check → V2
- Blacklist mail server check → V3

Si una feature no está aquí, **no se implementa**. Se agrega a TASKS.md primero y se actualiza este contrato con versión nueva.
