# ARCHITECTURE.md — Cómo encajan las piezas

## Vista general

```
┌─────────────────────────────────────────────────┐
│           Samsung Galaxy Tab A8                 │
│  ─ Fully Kiosk Browser en landscape             │
│  ─ Tailscale Android conectado al tailnet       │
│  ─ Apunta a http://100.x.x.x:8080               │
│  ─ Pollea /api/v1/status cada 5s                │
└─────────────────────┬───────────────────────────┘
                      │ HTTP sobre Tailscale
                      │
┌─────────────────────▼───────────────────────────┐
│           VPS-MyRock (srv1386238)               │
│           Hetzner · Ubuntu 24.04                │
│           2 vCPU / 8 GB RAM / 96 GB disco       │
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │  Docker Compose project: noc-stack      │   │
│  │                                          │   │
│  │  ┌─────────────────┐  ┌───────────────┐ │   │
│  │  │  noc-api        │  │  noc-frontend │ │   │
│  │  │  FastAPI        │  │  nginx + html │ │   │
│  │  │  port 8000      │  │  port 80      │ │   │
│  │  └────────┬────────┘  └───────────────┘ │   │
│  │           │                              │   │
│  │  ┌────────▼────────┐                    │   │
│  │  │   SQLite        │                    │   │
│  │  │   /data/noc.db  │                    │   │
│  │  └─────────────────┘                    │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
│  Tailscale daemon (tailscaled)                  │
│  IP Tailscale: 100.x.x.x                        │
│  Otros containers ya existentes:                │
│  ─ evolution-api, evolution-api-v2              │
│  ─ infra (nginx-proxy + certbot)                │
│  ─ myrock-stack, n8n, naibi-stack               │
└──────┬──────────────────────────────────────────┘
       │ SSH con llave dedicada
       │ (ControlMaster persistente)
       │
   ┌───┴────────┬──────────────┬──────────────┐
   │            │              │              │
┌──▼────┐  ┌────▼─────┐  ┌─────▼─────┐  ┌────▼──────┐
│ VPS   │  │ VPS      │  │ VPS       │  │ Internet  │
│ SUIG  │  │ OIC      │  │ Mail      │  │ público   │
│       │  │          │  │ (Mailcow) │  │ (para     │
│ Docker│  │ Docker   │  │ Docker    │  │  TLS, DNS,│
└───────┘  └──────────┘  └───────────┘  │  HTTP     │
                                         │  checks)  │
                                         └───────────┘
```

## Componentes

### 1. Tab A8 (cliente)

- Samsung Galaxy Tab A8 (Android 14)
- Fully Kiosk Browser apuntando a `http://100.x.x.x` (IP Tailscale de VPS-MyRock)
- Tailscale Android instalado y conectado
- Modo landscape forzado
- Wakelock activado (pantalla siempre encendida)
- Alimentación constante por USB-C

**Solo función**: renderizar HTML. No tiene credenciales. No tiene SSH keys. No tiene acceso a nada que no sea el HTTP de la API.

### 2. VPS-MyRock (servidor)

Servidor principal donde corre **todo** el stack del NOC.

#### 2.1. Tailscale daemon
- Instalado nativo en el host (no en container)
- Conectado al tailnet personal de Jorge
- Provee IP `100.x.x.x` por la que escucha el NOC

#### 2.2. Docker Compose project `noc-stack`

Vive aislado del resto de containers (red propia, volúmenes propios).

**Container `noc-api`** (FastAPI)
- Python 3.11+
- Escucha en `0.0.0.0:8000` dentro de la red Docker interna
- Publicado en `100.x.x.x:8000` (solo Tailscale)
- Levanta workers async para checks periódicos
- Lee/escribe SQLite
- Configuración con `docs_url=None, redoc_url=None, openapi_url=None`

**Container `noc-frontend`** (nginx + html)
- nginx alpine
- Sirve `index.html` + assets estáticos
- Escucha en `100.104.244.83:8080` (Tailscale, no público)
- Puerto 80 del host ya ocupado por nginx nativo → NOC usa 8080
- Proxy reverso de `/api/*` → `noc-api:8000` (Fase 3)

**Volume `noc-data`**
- Persiste `/data/noc.db` (SQLite)
- Backups locales automáticos

### 3. SSH hacia otros VPS

VPS-MyRock tiene una llave SSH **dedicada** para el NOC (no la personal de Jorge).

`~/.ssh/noc_collector_ed25519` con permisos `0600`. La llave pública se instala en:
- `suig-vps`: `/root/.ssh/authorized_keys` (con `command="..."` para restringir comandos)
- `vps-oic`: igual
- `cedh-mail`: igual

**SSH config en VPS-MyRock** (`~/.ssh/config`):
```
Host suig-vps vps-oic cedh-mail
    IdentityFile ~/.ssh/noc_collector_ed25519
    ControlMaster auto
    ControlPath ~/.ssh/cm-%r@%h:%p
    ControlPersist 10m
    ServerAliveInterval 30
```

ControlMaster mantiene una conexión persistente, así los comandos siguientes son ~50ms.

### 4. Comunicación

| Origen | Destino | Protocolo | Puerto | Sobre |
|---|---|---|---|---|
| Tab A8 | VPS-MyRock | HTTP | 80 | Tailscale |
| Tab A8 | noc-api | HTTP | 8000 (via nginx) | Tailscale |
| noc-api | suig-vps | SSH | 22 | Internet público (encriptado) |
| noc-api | vps-oic | SSH | 22 | Internet público (encriptado) |
| noc-api | cedh-mail | SSH | 22 | Internet público (encriptado) |
| noc-api | cedhsinaloa.org.mx | HTTPS | 443 | Internet público |
| noc-api | DNS resolvers (1.1.1.1) | DNS | 53 | Internet público |
| noc-api | SMTP/IMAP de cedh-mail | TCP | 587, 993 | Internet público |

## Flujo de un check (ejemplo: estado de SUIG)

```
1. noc-api worker se dispara cada 15s
   └─> http_check_worker.check("SUIG")

2. Worker hace GET https://suig.cedhsinaloa.org.mx/health
   ├─ timeout 5s
   ├─ verifica status code
   ├─ mide latencia
   └─ parsea respuesta JSON si /health expone más info

3. Worker actualiza la entrada en memoria:
   services["SUIG"] = {
       status: "ok",
       http_status: 200,
       latency_ms: 184,
       last_checked: <now>
   }

4. Worker persiste evento en SQLite si cambia de estado
   (transiciones ok->warning, warning->critical, etc.)

5. Endpoint GET /api/v1/status devuelve cache en memoria
   (TTL 5s, refrescado por workers)

6. Tab A8 pollea /api/v1/status cada 5s
   └─> recibe el estado actualizado
   └─> renderiza
```

## Flujo de un check con SSH (ejemplo: CPU de vps-oic)

```
1. metrics_worker se dispara cada 60s
   └─> ssh_collector.get_metrics("vps-oic")

2. SSH reusa la conexión ControlMaster persistente
   └─> ejecuta: cat /proc/loadavg; free -m; df -h /
   └─> latencia ~50ms (conexión ya abierta)

3. Parser convierte salida en metrics dict
   └─> {cpu_percent: 8, ram_percent: 62, ...}

4. Igual que el flujo anterior:
   ├─ Actualiza memoria
   ├─ Persiste cambio si pasa umbrales
   └─ Disponible en /api/v1/status
```

## Decisiones técnicas clave

### Por qué FastAPI y no Flask/Django
- Async nativo (importante para muchos checks paralelos)
- Validación automática con Pydantic
- Generación de OpenAPI (aunque la desactivemos en producción, sirve en dev)

### Por qué SQLite y no Postgres
- v1 maneja <10,000 eventos al mes
- Sin servidor separado, menos superficie
- Backup = copiar 1 archivo
- Migrar a Postgres en V2 si se necesita, vía Alembic

### Por qué HTML vanilla y no React/Vue
- 1 página, sin routing
- 1 desarrollador
- Tab A8 con 3 GB de RAM y procesador modesto
- Carga rápida sin build pipeline

### Por qué nginx separado en lugar de FastAPI sirviendo estáticos
- Separación de concerns
- nginx mejor en caching de assets
- Permite swap del frontend sin tocar la API

### Por qué SSH y no Tailscale-en-todos-los-VPS
- SSH funciona hoy sin pedir permisos
- Tailscale en VPS institucionales requiere autorización
- Latencia equivalente con ControlMaster
- Fácil upgrade a Tailscale después si se decide

### Por qué Tailscale para el dashboard y no Cloudflare Access
- Más simple: 1 app por dispositivo
- No requiere DNS público
- Funciona sin internet si los 2 dispositivos están en mesh
- Mejor experiencia móvil

## Lo que NO está en este diseño

- **No hay agentes locales** en los VPS monitoreados (V1.5 si hace falta)
- **No hay WebSockets** (V2)
- **No hay queue/Redis** (V2 si async no alcanza)
- **No hay reverse proxy externo** (nginx interno del noc-stack es suficiente)
- **No hay clustering** (1 instancia de FastAPI es suficiente)
- **No hay HTTPS para el frontend** (Tailscale ya es encriptado end-to-end)
