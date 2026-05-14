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

  // Campos de presentación humana (V1 operativo)
  title: string;              // Título humano en español, ej: "PagoKids no responde correctamente"
  description: string;        // Contexto: qué se observa, qué responde y qué no
  diagnosis: string;          // Diagnóstico probable y acción sugerida (después del →)
  impact_label: ImpactLabel;  // Badge de impacto

  // Campos técnicos
  first_error: string | null; // Error técnico crudo (HTTP code, exception, etc)
  duration_seconds: number;   // Cuánto lleva activo (calculado en cada update)
  duration_human: string;     // Formato amigable: "14m", "2h 18m", "3d 4h"
}

type ImpactLabel =
  | "Afecta usuarios públicos"
  | "Afecta operación interna"
  | "Sin impacto operativo"
  | "Solo monitoreo";

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
  "recent_incidents": [
    {
      "id": "inc_20260512_201432",
      "started_at": "2026-05-12T20:14:32-07:00",
      "resolved_at": null,
      "status": "open",
      "severity": "high",
      "target_type": "service",
      "target_name": "pagokids",
      "title": "PagoKids no responde correctamente",
      "description": "Cloudflare devuelve 520. El VPS MyRock está vivo y otros servicios responden normal.",
      "diagnosis": "Probable: problema entre Cloudflare y el origen. Revisar nginx del contenedor pagokids-web y logs.",
      "impact_label": "Afecta usuarios públicos",
      "first_error": "HTTP 520 Cloudflare",
      "duration_seconds": 840,
      "duration_human": "14m"
    }
  ]
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

## Generación de incidentes con diagnóstico

El aggregator (en backend) es responsable de transformar fallos técnicos en incidentes con presentación humana. Esto es **lógica de la API**, no del frontend.

### Reglas de generación

Cuando un check transiciona a estado `critical` o `down`, el aggregator:

1. Crea entrada en tabla `incidents` con `status: open`
2. Llena los campos humanos según **mapeo por tipo de error**:

| Error técnico | title | description | diagnosis | impact_label |
|---|---|---|---|---|
| HTTP 5xx | `{servicio} no responde correctamente` | `Servidor devuelve {code}. {servidor host} está {status}.` | `Revisar logs del contenedor {servicio}-{role} y nginx.` | `Afecta usuarios públicos` si criticality=high |
| HTTP timeout | `{servicio} no responde` | `Timeout tras {N}s. {servidor host} está {status}.` | `Verificar que el servicio está vivo (docker ps) y nginx escucha.` | según criticality |
| Cloudflare 520 | `{servicio} no responde correctamente` | `Cloudflare devuelve 520. El VPS está vivo.` | `Probable: problema entre Cloudflare y origen. Revisar nginx del contenedor {servicio}-web.` | `Afecta usuarios públicos` |
| HTTP 301 inesperado | `{servicio} redirige inesperadamente` | `Devuelve 301 en lugar de 200. Servicio funcional pero comportamiento inesperado.` | `Verificar si fue cambio intencional. Revisar config y logs.` | `Sin impacto operativo` |
| SSH falla | `Agente {servidor} no responde` | `No se pudo establecer conexión SSH. El servidor puede estar caído o haber rechazado la conexión.` | `Verificar estado del servidor en panel del proveedor.` | `Solo monitoreo` |
| SSL <7d | `Certificado {dominio} vence en {N} días` | `Let's Encrypt vence el {fecha}.` | `Renovar manualmente con certbot o esperar renovación automática.` | según criticality del servicio |
| DNS missing | `Falta registro {tipo} en {dominio}` | `No se encontró registro {tipo} consultando {resolver}.` | `Verificar configuración DNS en proveedor.` | `Afecta operación interna` |
| Disco >90% | `{servidor} casi sin espacio` | `Disco al {N}%, quedan {M} GB.` | `Limpiar logs, backups viejos o expandir volumen.` | `Solo monitoreo` |

### Diagnóstico contextual (usa otros checks)

El diagnóstico debe **correlacionar señales**. Ejemplo:
- Si servicio HTTP devuelve 520 **Y** ping al VPS host responde **Y** otros servicios del mismo VPS responden → diagnosis: "problema entre Cloudflare y el origen"
- Si servicio HTTP devuelve timeout **Y** ping al VPS host **falla** → diagnosis: "VPS host inalcanzable; problema de infraestructura"
- Si servicio HTTP devuelve 5xx **Y** deploy reciente en mismo repo → diagnosis: "deploy reciente ({sha}) puede haber introducido el problema; revisar logs post-deploy"

Esta lógica de correlación vive en `app/aggregator.py` con tests específicos.

### Cuándo NO generar incidente

- Transiciones `warning → ok` no generan incidente
- Transiciones `ok → warning` generan incidente solo si la métrica está en warning por >5 minutos sostenidos (anti-flapping)
- Servicios con `criticality: low` solo generan incidente al pasar a `down`, no a `warning`

---

## Lo que NO está en este contrato (no implementar en V1)

- WebSocket de logs en vivo → V2
- Gráficas históricas 24h → V2
- Endpoints `POST /api/v1/action/*` → V3 con PIN+TOTP
- Heatmap 5xx por hora → V2
- DKIM check → V2
- Blacklist mail server check → V3

Si una feature no está aquí, **no se implementa**. Se agrega a TASKS.md primero y se actualiza este contrato con versión nueva.
