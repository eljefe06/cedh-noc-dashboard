# TASKS.md — Lista de tareas

> **Fuente única de verdad** sobre dónde está el proyecto.
>
> Convención de estado:
> - `[ ]` Pendiente
> - `[~]` En progreso
> - `[x]` Completada
> - `[!]` Bloqueada (con explicación en línea)
>
> Cada tarea completada debe marcarse en el mismo commit que la implementa.
>
> Última actualización: 2026-05-13 (Phase 3 backend completa, Tab A8 Tailscale instalado)

---

## FASE 0 · Setup inicial

### 0.1 Documentación base

- [x] Crear `README.md`
- [x] Crear `docs/PROJECT.md`
- [x] Crear `docs/ARCHITECTURE.md`
- [x] Crear `docs/INVENTORY.md`
- [x] Crear `docs/API_CONTRACT.md`
- [x] Crear `docs/DESIGN.md`
- [x] Crear `docs/SECURITY.md`
- [x] Crear `docs/CONVENTIONS.md`
- [x] Crear `docs/GLOSSARY.md`
- [x] Crear `CLAUDE.md`
- [x] Crear `docs/TASKS.md` (este archivo)

### 0.2 Cuenta de Tailscale

- [x] Crear cuenta en tailscale.com (auth con Google o GitHub)
- [x] Verificar plan free (hasta 100 dispositivos)
- [x] Definir nombre del tailnet → `taild92bae.ts.net`
- [~] Configurar ACL inicial — dejada en default; refinar cuando haya devices con tags (Fase 0.3+)
- [x] Activar MagicDNS

### 0.3 Tailscale en VPS-MyRock

- [x] SSH a srv1386238 con credenciales actuales
- [x] Instalar Tailscale: `curl -fsSL https://tailscale.com/install.sh | sh` → v1.98.1
- [x] Conectar: `tailscale up`
- [x] Anotar IP Tailscale asignada → `100.104.244.83`
- [x] Actualizar `docs/INVENTORY.md` con la IP Tailscale real
- [x] Probar `ping` interno a la IP Tailscale desde el mismo host → 0.093ms, 0% loss

### 0.4 Tailscale en Tab A8

- [x] Esperar que termine actualización de Android
- [x] Play Store → instalar Tailscale Android
- [x] Login con mismo usuario que VPS-MyRock
- [x] Tab A8 aparece en tailnet → `galaxy-tab-a8` / `100.121.75.52`
- [x] Dashboard visible desde Tab A8 en `http://100.104.244.83:8080` ✅

### 0.5 Inicializar repositorio

- [x] `git init` en local
- [x] Crear `.gitignore` con: `.env`, `*.key`, `*.pem`, `noc.db`, `__pycache__/`, `node_modules/`, `.venv/`
- [x] Primer commit con docs completas
- [x] Crear repo remoto → https://github.com/eljefe06/cedh-noc-dashboard (privado)
- [x] Push inicial
- [x] Configurar branch protection en `main` (require PR review)

---

## FASE 1 · Frontend mock funcional

> Objetivo: Tener un dashboard navegable con datos ficticios que se ve **idéntico** a como debe verse en producción. Sin backend real.

### 1.1 Estructura del frontend

- [ ] Crear carpeta `frontend/`
- [ ] Crear `frontend/index.html` con estructura semántica vacía
- [ ] Crear `frontend/css/main.css` con variables CSS de `docs/DESIGN.md`
- [ ] Crear `frontend/js/main.js` (entry point)
- [ ] Crear `frontend/js/api.js` (capa de fetch)
- [ ] Crear `frontend/js/render.js` (lógica de renderizado)
- [ ] Crear `frontend/js/sparkline.js` (SVG sparklines)
- [ ] Crear `frontend/js/status-colors.js` (mapeo estado → CSS class)
- [ ] Crear `frontend/mock-data/status.json` con ejemplo del contrato
- [ ] Descargar e incluir JetBrains Mono local en `frontend/assets/fonts/`

### 1.2 Implementación visual

- [ ] Layout horizontal completo (header + top row + services grid + bottom row + footer)
- [ ] Header con pulse animado y métricas globales
- [ ] VPS cards (4 cards) con métricas CPU/RAM/DISK/NET y barras de progreso
- [ ] Service cards (8 cards) con status pill, sparkline, metadata
- [ ] Bottom panel: logs (con tags coloreados)
- [ ] Bottom panel: SSL expirations
- [ ] Bottom panel: git deploys recientes
- [ ] Footer con Tailscale status y versión
- [ ] HUD brackets en esquinas de cards y panels
- [ ] Scanlines sutiles en fondo
- [ ] Glow real con box-shadow en colores neón
- [ ] Animaciones: pulse (header) y blink (servicio caído)
- [ ] Estado vacío para paneles sin datos
- [ ] Mensaje "rota la tablet a horizontal" si portrait

### 1.3 Lógica de datos mock

- [ ] Cargar `mock-data/status.json` en cada poll
- [ ] Implementar polling cada 5 segundos
- [ ] Renderizar status completo en primer load
- [ ] Re-render solo elementos cambiados (diff básico)
- [ ] Manejar errores de carga con overlay "API SIN RESPUESTA"
- [ ] Calcular `overall_status` correctamente según reglas del contrato
- [ ] Mapear estados a clases CSS correctamente
- [ ] Mostrar sparklines con datos del mock (array de números)
- [ ] Mostrar incidents con tiempos relativos ("hace 4m")

### 1.4 Variaciones de mock

- [ ] Mock 1: todo OK
- [ ] Mock 2: 1 servicio warning, 1 critical
- [ ] Mock 3: 1 servidor agent_unreachable
- [ ] Mock 4: certificado SSL crítico (<7d)
- [ ] Mock 5: incidente activo nuevo
- [ ] Script local que rota entre mocks cada 30s para preview

### 1.5 Validación local

- [ ] Abrir `frontend/index.html` directo en Chrome desktop
- [ ] Verificar que se ve idéntico al diseño aprobado
- [ ] Verificar polling funciona y re-renders no parpadean
- [ ] Validar accesibilidad básica (Lighthouse)
- [ ] Probar con throttling de red 3G slow para ver carga inicial

---

## FASE 2 · Tailscale + Deploy del mock en VPS-MyRock

> Objetivo: Ver el dashboard mock **en la Tab A8 real** vía Tailscale.

### 2.1 Preparar nginx en VPS-MyRock

- [x] Identificar si nginx existente puede agregar virtual host → no conveniente (nginx nativo en 0.0.0.0:80)
- [x] Crear nginx específico en `noc-stack` (contenedor Docker)
- [x] Configurar bind explícito a IP Tailscale → `100.104.244.83:8080` (8080 porque 80 ya ocupado)
- [x] Verificar UFW: NOC no expuesto en IP pública ✓

### 2.2 Docker Compose para noc-stack (mock-only)

- [x] Crear `docker-compose.yml` en raíz del repo
- [x] Service `noc-frontend`: nginx alpine sirviendo `frontend/`
- [x] Volúmenes: montar `frontend/` read-only
- [x] Red: docker network propia `noc-net`
- [x] Restart policy: `unless-stopped`
- [x] Logging driver: json-file con rotación

### 2.3 Deploy del mock

- [x] Clonar repo en VPS-MyRock → `/opt/noc`
- [x] `docker compose up -d noc-frontend` → HTTP 200 OK
- [x] Verificar que escucha en IP Tailscale → `100.104.244.83:8080`
- [x] Probar desde Mac con Tailscale → dashboard visible ✓

### 2.4 Configurar Tab A8

- [ ] Instalar Fully Kiosk Browser (gratis para uso básico)
- [ ] Configurar URL inicial: `http://100.x.x.x`
- [ ] Activar fullscreen mode
- [ ] Bloquear orientación en landscape
- [ ] Wakelock: pantalla siempre encendida
- [ ] Auto-restart en 4 AM
- [ ] Prevenir descarga y enlaces externos
- [ ] Configurar modo desarrollador Android: mantener encendido al cargar
- [ ] Brillo entre 35-50%
- [ ] Bloquear notificaciones del sistema

### 2.5 Validación en hardware real

- [ ] Abrir dashboard en Tab A8
- [ ] Validar contraste y legibilidad en condiciones reales de oficina
- [ ] Validar que no se calienta la tablet con uso prolongado (1h)
- [ ] Validar que polling no consume batería excesivamente
- [ ] Validar densidad visual a distancia normal de monitor
- [ ] Fotos del setup final para documentación

---

## FASE 3 · Backend FastAPI con datos mock

> Objetivo: Reemplazar el JSON estático con una API FastAPI que aún devuelve datos mock pero estructurados correctamente.

### 3.1 Estructura del backend

- [x] Crear carpeta `backend/`
- [x] Crear `pyproject.toml` con dependencies (fastapi, uvicorn, pydantic, pydantic-settings, httpx, asyncssh, cryptography, sqlite3 stdlib)
- [x] Crear estructura: `app/`, `tests/`, `Dockerfile`
- [x] Crear `.env.example` con todas las variables
- [x] Crear `backend/app/__init__.py`

### 3.2 Modelos Pydantic

- [x] Crear `app/models.py` con todos los tipos del contrato (con Field validators ge/le en Metrics)
- [x] Status, Server, Service, SslCert, Backup, Deploy, DnsCheck, Incident, DockerInfo, DockerContainer
- [x] Tests: 9 tests pasando (test_models.py)

### 3.3 Config

- [x] Crear `app/config.py` con `Settings` de pydantic-settings
- [x] Cargar desde `.env`
- [x] Properties helpers: `cors_origins_list`, `dns_resolvers_list`

### 3.4 App FastAPI mínima

- [x] Crear `app/main.py` con FastAPI + lifespan
- [x] Middleware: CORS desde IPs configuradas en .env
- [x] Router `/api/v1`
- [x] Endpoint `GET /api/v1/health`
- [x] Endpoint `GET /api/v1/status` — sirve mock desde cache SQLite (seeded en startup)
- [x] Endpoints `/api/v1/incidents/recent`, `/incidents/open`, `/dns`

### 3.5 Storage SQLite

- [x] Crear `app/storage.py` con wrapper
- [x] Schema: tablas `events`, `incidents`, `metric_snapshots`, `status_cache`
- [x] Migrations simples al startup
- [x] Funciones: cache_get/set, incident_open/resolve, incidents_recent/open

### 3.6 Containerizar

- [x] `backend/Dockerfile` multi-stage Python 3.11.10-slim-bookworm
- [x] Usuario no-root (nocapi uid 1001)
- [x] Health check del container
- [x] Agregar `noc-api` a `docker-compose.yml`
- [x] Nginx del frontend proxy `/api/*` → `noc-api:8000`
- [ ] Verificar imagen pesa <200MB (pendiente build en VPS)

### 3.7 Frontend → API

- [x] `frontend/js/app.js` → llama `/api/v1/status` cuando protocol === 'http:'
- [x] Fallback automático a mocks cuando protocol === 'file:'
- [~] **Probar end-to-end: tablet → nginx → api → JSON** (pendiente deploy en VPS)

---

## FASE 4 · Discovery completo

> Objetivo: Tener datos reales de los 3 VPS faltantes y actualizar el inventario.

### 4.1 Script discovery v2

- [ ] Tomar el script v2 que Jorge va a entregar (mejorado del v1)
- [ ] Colocarlo en `scripts/discovery-v2.sh`
- [ ] Documentar uso en cabecera del script
- [ ] Probar en VPS-MyRock con v2 (sobrescribe el v1 anterior)

### 4.2 SSH desde VPS-MyRock hacia los otros 3

- [x] Generar llave dedicada `noc_collector_ed25519` en VPS-MyRock
- [x] Copiar llave pública a VPS-SUIG `authorized_keys` (root@187.124.152.86) ✅
- [x] Copiar llave pública a VPS-OIC `authorized_keys` (root@31.220.58.97) ✅
- [x] Copiar llave pública a VPS-Mail `authorized_keys` (jyanagui@100.118.231.85 via Tailscale) ✅
- [x] Probar SSH desde VPS-MyRock → 3/3 OK
- [ ] Configurar SSH config con ControlMaster en VPS-MyRock

### 4.3 Discovery en VPS-SUIG

- [x] Discovery vía SSH completado 2026-05-13
- [x] Actualizar `INVENTORY.md` con datos reales ✅
- Proyectos: suig-cedh, cedh-sinaloa, evolution-api (v1 interno)
- Dominios: cedhsinaloa.org.mx, suig., buzon. (todos en vps-suig)
- [ ] Verificar SSL de suig. y buzon. subdomains
- [ ] Confirmar cedhs.xyz

### 4.4 Discovery en VPS-OIC

- [x] Discovery vía SSH completado 2026-05-13
- [x] Actualizar `INVENTORY.md` con datos reales ✅
- Proyectos: sistema-declaraciones, sier, denuncia-oic, oic
- Dominios: declaraciones., oic., sier.cedhsinaloa.org.mx
- PM2: oic-portal, oic-api, oic-panel (15d uptime)
- ⚠️ declaraciones.cedhsinaloa.org.mx sin SSL — pendiente informar a Jorge

### 4.5 Discovery en VPS-Mail

- [ ] Correr `scripts/discovery-v2.sh`
- [ ] Guardar JSON
- [ ] Pegar a Jorge para review
- [ ] Actualizar `docs/INVENTORY.md`

### 4.6 Verificación de health endpoints

- [ ] Listar todos los servicios HTTP a monitorear
- [ ] Para cada uno: verificar si `/health` existe o si hay que crearlo
- [ ] Decidir con Jorge cuáles agregar (puede ser bloqueador)

### 4.7 noc-readonly-shell

- [ ] Crear script en `scripts/noc-readonly-shell`
- [ ] Instalar en los 3 VPS monitoreados
- [ ] Configurar `command=` en `authorized_keys`
- [ ] Probar que solo comandos permitidos funcionan
- [ ] Documentar lista de comandos permitidos

---

## FASE 5 · Collectors reales

> Objetivo: Reemplazar mocks con datos reales, collector por collector.

### 5.1 Collector base

- [ ] Crear `app/collectors/base.py` con interface `Collector`
- [ ] Worker async que ejecuta collectors según `poll_interval`
- [ ] Cache en memoria con TTL
- [ ] Persistencia de transiciones de estado en SQLite

### 5.2 HTTP Collector

- [ ] Crear `app/collectors/http.py`
- [ ] Función `check_http(url, timeout) → CheckResult`
- [ ] Mide latency, parsea status code
- [ ] Si `/health` devuelve JSON, parsearlo
- [ ] Tests con servidor mock local
- [ ] Conectar al servicio MyRock (vive en mismo VPS, prueba interna)
- [ ] Expandir a todos los servicios HTTP de `INVENTORY.md`

### 5.3 SSL Collector

- [ ] Crear `app/collectors/ssl.py`
- [ ] Función `check_ssl(domain) → SslCert`
- [ ] Usa Python `ssl` module o `cryptography`
- [ ] Calcula días restantes
- [ ] Tests con dominio conocido
- [ ] Iterar sobre lista de dominios de `INVENTORY.md`

### 5.4 DNS Collector

- [ ] Crear `app/collectors/dns.py`
- [ ] Usar `dnspython`
- [ ] Funciones: `check_mx`, `check_spf`, `check_dmarc`, `check_a`, `check_ptr`
- [ ] Función `check_smtp_starttls`, `check_imap_tls`
- [ ] Tests
- [ ] Iterar sobre lista de checks DNS de `INVENTORY.md`

### 5.5 SSH Collector

- [ ] Crear `app/collectors/ssh.py`
- [ ] Usa `asyncssh` con ControlMaster path
- [ ] Función `get_metrics(server) → MetricsDict` ejecutando `cat /proc/loadavg; free -m; df -h /`
- [ ] Parser robusto de outputs
- [ ] Tests con mock SSH
- [ ] Conectar a VPS-SUIG y verificar
- [ ] Conectar a VPS-OIC
- [ ] Conectar a VPS-Mail

### 5.6 Docker Collector (V1)

- [ ] Crear `app/collectors/docker_ssh.py`
- [ ] Ejecuta `docker ps -a --format json` por SSH
- [ ] Parser que devuelve lista de containers
- [ ] Tests
- [ ] Conectar a los servidores con Docker

### 5.7 Backups Collector

- [ ] Crear `app/collectors/backups.py`
- [ ] Configurar rutas de backups por servidor (en `INVENTORY.md`)
- [ ] Ejecuta `ls -la <ruta>` por SSH y parsea fecha del último archivo
- [ ] Tests

### 5.8 Deploys Collector

- [ ] Crear `app/collectors/deploys.py`
- [ ] Configurar rutas de repos git
- [ ] Ejecuta `git -C <path> log -1 --format='%h %ai %an %s'` por SSH
- [ ] Parser
- [ ] Tests

### 5.9 Status aggregator

- [ ] Crear `app/aggregator.py` que junta todos los collectors
- [ ] Aplica reglas de `overall_status` del contrato
- [ ] Aplica reglas de `server.status`
- [ ] Genera/cierra incidentes según transiciones de estado
- [ ] Tests de las reglas con casos del contrato

### 5.10 End-to-end con datos reales

- [ ] Endpoint `/api/v1/status` ya devuelve datos reales
- [ ] Frontend muestra estado real
- [ ] Validar en Tab A8

---

## FASE 6 · Producción

### 6.1 Hardening

- [ ] Bearer token en `.env`, validado en cada request
- [ ] Rate limiting básico (no más de 60 reqs/min por IP)
- [ ] Logs estructurados JSON
- [ ] Log redaction de secrets
- [ ] Backup nightly de SQLite

### 6.2 Observability del propio NOC

- [ ] Health endpoint robusto que verifica: collectors corriendo, DB accesible, último check exitoso
- [ ] Métricas internas: cuántos checks por minuto, latencia de cada collector
- [ ] Self-monitoring: si un collector falla 3 veces, generar incidente

### 6.3 Documentación operativa

- [ ] `docs/OPERATIONS.md`: cómo redeployar, cómo agregar servicio, cómo rotar llaves
- [ ] `docs/TROUBLESHOOTING.md`: errores comunes y soluciones
- [ ] README final actualizado

### 6.4 Checklist final pre-producción

Ver `docs/SECURITY.md` sección "Checklist de seguridad pre-producción".

---

## FASE 7 (V1.5) · Módulo Docker enriquecido

- [ ] Lectura completa de containers con `docker inspect`
- [ ] CPU/RAM por container con `docker stats`
- [ ] Detección de containers `unhealthy` y propagación a servicios
- [ ] Vista detallada Docker por servidor

---

## FASE 8 (V2) · Drill-down y logs en vivo

- [ ] Vista detallada por servicio (modal)
- [ ] Gráficas históricas 24h por servicio
- [ ] WebSocket para logs en streaming
- [ ] Heatmap 5xx por hora
- [ ] DKIM check

---

## FASE 9 (V3) · Acciones protegidas

- [ ] PIN local para activar modo acciones
- [ ] TOTP como segundo factor
- [ ] Endpoints `POST /api/v1/action/*`
- [ ] Whitelist estricta de acciones permitidas
- [ ] Audit log de cada acción
- [ ] Confirmación doble en destructivas
- [ ] Push notifications a tablet en alertas críticas
- [ ] Modal de reinicio de VPS (con PIN + confirmación doble)

---

## Decisiones tomadas durante la implementación

> Sección viva. Se agrega cada decisión no obvia con fecha y contexto.

- **2026-05-12**: Confirmado que SUIG, OIC y Mailcow corren en Docker. El módulo Docker queda en V1 (no V1.5).
- **2026-05-12**: VPS-MyRock (srv1386238) tiene 2 cores con load ~1.0, se ajustan polling intervals a 15s/60s para no saturar.
- **2026-05-12**: Tailscale elegido como red privada en lugar de Cloudflare Access por simplicidad.
- **2026-05-12**: Opción A (SSH desde noc-api hacia VPS monitoreados, sin instalar agentes) elegida por mínima invasividad.

---

## Bloqueadores actuales

> Cosas que impiden avanzar. Resolver antes de progresar.

- [ ] **Dominios OIC no confirmados** (declaraciones, denuncias, ser-cedh) — bloquea Fase 5.2 para esos servicios
- [ ] **No confirmado si `/health` existe en cada sistema** — puede bloquear Fase 4.6
- [ ] **SERVERS_CONFIG en .env** del VPS necesita actualizarse con IPs/users reales antes de Phase 5

---

## Backlog (ideas no priorizadas)

> Se agregan aquí; cuando se decida implementar, se mueve a fase numerada.

- Status page público separado de cedhsinaloa.org.mx
- Integración con WhatsApp via Evolution API para alertas críticas
- Auto-rotación de llaves SSH del NOC cada 6 meses
- Dashboard para PagoKids con métricas específicas (transacciones/min, errores Stripe)
- Métricas de SUIG: quejas por hora, distribución por visitador (sería un dashboard distinto)
- Export de incidentes a CSV/PDF para reportes
- Modo "demo" del NOC para mostrar a colegas sin exponer datos reales
- Detección automática de cambios en infraestructura (nuevo container, nuevo dominio SSL, etc.)
- Integración con Cloudflare API para purge automático cuando se detecte stale cache
- Mobile-responsive view (en otro dispositivo, no la tablet)
