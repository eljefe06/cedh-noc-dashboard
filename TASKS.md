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
> Última actualización: 2026-05-14

---

## FASE 0 · Setup inicial

### 0.1 Documentación base

- [x] Crear `README.md`
- [x] Crear `PROJECT.md`
- [x] Crear `ARCHITECTURE.md`
- [x] Crear `INVENTORY.md`
- [x] Crear `API_CONTRACT.md`
- [x] Crear `DESIGN.md`
- [x] Crear `SECURITY.md`
- [x] Crear `CONVENTIONS.md`
- [x] Crear `GLOSSARY.md`
- [x] Crear `CLAUDE.md`
- [x] Crear `TASKS.md` (este archivo)

### 0.2 Cuenta de Tailscale

- [x] Crear cuenta en tailscale.com
- [x] Verificar plan free (hasta 100 dispositivos)
- [x] Definir nombre del tailnet → `taild92bae.ts.net`
- [~] Configurar ACL inicial — default por ahora; refinar cuando haya tags
- [x] Activar MagicDNS

### 0.3 Tailscale en VPS-MyRock

- [x] SSH a srv1386238
- [x] Instalar Tailscale → v1.98.1
- [x] Conectar: `tailscale up`
- [x] IP Tailscale asignada → `100.104.244.83`
- [x] Actualizar `INVENTORY.md` con la IP Tailscale real
- [x] Ping interno verificado

### 0.4 Tailscale en Tab A8

- [x] Play Store → instalar Tailscale Android
- [x] Login con mismo usuario que VPS-MyRock
- [x] Tab A8 en tailnet → `galaxy-tab-a8` / `100.121.75.52`
- [x] Dashboard visible desde Tab A8 ✅

### 0.5 Inicializar repositorio

- [x] `git init` en local
- [x] Crear `.gitignore`
- [x] Primer commit con docs completas
- [x] Repo remoto → https://github.com/eljefe06/cedh-noc-dashboard (privado)
- [x] Push inicial
- [x] Branch protection en `main`

---

## FASE 1 · Frontend v2 (diseño operativo)

> Objetivo: Implementar el dashboard con el diseño operativo v2 — el que responde las 4 preguntas.
> El frontend v1 existe pero usa el diseño viejo (uniformidad democrática). Esta fase lo reemplaza.
>
> **Referencia visual**: `frontend/dashboardv2.html` en el repo.

### 1.1 Estructura del frontend

- [x] Crear carpeta `frontend/`
- [x] Crear `frontend/index.html`
- [x] Crear `frontend/css/main.css`
- [x] Crear `frontend/mock-data/status.json`
- [x] Crear `frontend/assets/fonts/` con JetBrains Mono
- [x] Crear `frontend/js/render-incidents.js` (bloque prominente de incidentes activos)
- [x] Crear `frontend/js/render-services.js` (chips de servicios)
- [x] Crear `frontend/js/render-infra.js` (VPS cards compactas)
- [x] Crear `frontend/js/render-panels.js` (paneles operativos)
- [x] Crear `frontend/js/duration.js` (formateo "14m", "2h 18m")
- [x] Actualizar `frontend/js/status-colors.js`

### 1.2 Implementación visual (layout operativo v2)

- [x] **Status bar**: 3 contadores grandes (crítico, advertencia, ok) + uptime/hora
- [x] Contador crítico parpadea (`pulse-crit`) cuando >0
- [x] **Bloque incidentes activos** con border-left 4px del color de severidad
- [x] Tag UPPERCASE de severidad en cada incidente
- [x] Título humano (13px) + descripción (11px secondary)
- [x] Línea de diagnóstico con `→ ` cyan
- [x] Duración prominente (18px) a la derecha
- [x] Badge de impacto explícito ("Afecta usuarios públicos", etc.)
- [x] **Sección "// servicios públicos"** con 8 chips compactos
- [x] Border-top 3px del color de estado en cada chip (sin pill)
- [x] **Sección "// infraestructura"** con 4 VPS cards horizontales
- [x] Stats inline: `cpu N  ram N  dsk N`, color cambia si warn/crit
- [x] Sin barras de progreso
- [x] **Paneles operativos** (3 columnas): últimos cambios, certificados, pendientes hoy
- [x] Footer con Tailscale status
- [x] Scanlines en fondo del screen

### 1.3 Estados especiales

- [x] Sin incidentes activos: mensaje compacto verde `✓ Sin incidentes activos`
- [x] API sin respuesta: overlay sin reemplazar último estado conocido
- [x] Portrait: mensaje `↻ ROTA LA TABLET A HORIZONTAL`

### 1.4 Lógica de datos

- [x] Polling cada 5 segundos a `/api/v1/status`
- [x] Calcular contadores del header desde los datos (crítico/advertencia/ok por tipo)
- [x] Recalcular `duration_human` cliente-side cada poll
- [x] Re-render diff básico (no parpadeo)
- [x] Detectar orientación de pantalla

### 1.5 Mocks v2

- [x] Mock 1: todo OK (estado vacío visible)
- [x] Mock 2: 1 critical + 1 warning (como el preview)
- [x] Mock 3: servidor agent_unreachable
- [x] Mock 4: SSL crítico (<7d) → aparece como incidente
- [x] Mock 5: RAM crítica en MyRock (warning + recomendación)

### 1.6 Validación

- [ ] Abrir en Chrome desktop — verificar idéntico a `dashboardv2.html`
- [ ] Verificar en Tab A8 real
- [ ] Duración de incidente sube cliente-side correctamente

---

## FASE 2 · Tailscale + Deploy del mock en VPS-MyRock

### 2.1–2.3 Docker + nginx

- [x] nginx en Docker bind a IP Tailscale `100.104.244.83:8080`
- [x] `docker-compose.yml` con noc-frontend
- [x] Deploy del frontend en `/opt/noc` en VPS-MyRock

### 2.4 Configurar Tab A8

- [x] Instalar Fully Kiosk Browser
- [x] URL: `http://100.104.244.83:8080`
- [x] Fullscreen landscape
- [x] Wakelock encendido
- [ ] Auto-restart a las 4 AM
- [ ] Brillo 35-50% configurado

### 2.5 Validación en hardware real

- [~] Dashboard carga en Tab A8 ✅ (verificado con datos reales)
- [ ] Validar contraste y legibilidad en oficina
- [ ] Validar temperatura tablet 1h
- [ ] Fotos del setup final

---

## FASE 3 · Backend FastAPI con datos mock

- [x] `backend/` con FastAPI + uvicorn + Pydantic v2
- [x] `app/models.py` — todos los tipos del contrato
- [x] `app/config.py` — pydantic-settings
- [x] `app/main.py` — FastAPI + lifespan + scheduler
- [x] `app/storage.py` — SQLite (incidents, cache, events)
- [x] `app/routers/status.py` — endpoints `/api/v1/status`, `/health`, `/incidents/*`, `/dns`
- [x] `backend/Dockerfile` multi-stage, usuario root (V1)
- [x] noc-api en `docker-compose.yml`, nginx proxy `/api/` → noc-api
- [x] Frontend llama `/api/v1/status` cuando protocol=http

---

## FASE 4 · Discovery completo

- [x] Llave SSH dedicada `noc_collector_ed25519` generada en VPS-MyRock
- [x] Llave copiada a VPS-SUIG (root@187.124.152.86) ✅
- [x] Llave copiada a VPS-OIC (root@31.220.58.97) ✅
- [x] Llave copiada a VPS-Mail (jyanagui@100.118.231.85 vía Tailscale) ✅
- [x] Llave agregada al propio VPS-MyRock authorized_keys ✅ (2026-05-14)
- [x] Discovery VPS-SUIG completado → INVENTORY.md actualizado
- [x] Discovery VPS-OIC completado → INVENTORY.md actualizado
- [x] Discovery VPS-Mail completado → Tailscale instalado → INVENTORY.md actualizado
- [x] Health endpoints verificados en todos los servicios
- [ ] Configurar SSH ControlMaster en VPS-MyRock
- [ ] noc-readonly-shell (script de shell restringido para los VPS monitoreados)

---

## FASE 5 · Collectors reales

> Collectors implementados y corriendo. API devuelve datos reales de 4/4 servidores.

### 5.1–5.6 Collectors implementados ✅

- [x] `app/collectors/base.py` — CheckResult, MetricsResult, DockerResult
- [x] `app/collectors/http.py` — check_http, check_smtp_starttls, check_imap_tls
- [x] `app/collectors/ssh_metrics.py` — asyncssh + python3 one-liner (cpu/ram/disk/net/uptime)
- [x] `app/collectors/ssl.py` — TLS cert check, calcula días restantes
- [x] `app/collectors/dns.py` — dnspython: mx, spf, dmarc, a, ptr
- [x] `app/collectors/docker_ssh.py` — docker ps via SSH, state/health/uptime
- [x] `app/service_config.py` — 4 servidores, todos los servicios, SSL domains, DNS checks
- [x] `app/scheduler.py` — asyncio polling: HTTP 15s, metrics/docker 60s, SSL 6h, DNS 1h
- [x] `app/aggregator.py` — overall_status y server_status según reglas del contrato

### 5.7–5.8 Collectors diferidos

- [ ] `app/collectors/backups.py` — diferido a V1.5
- [ ] `app/collectors/deploys.py` — diferido a V1.5

### 5.9 Status aggregator + Incident generator

- [x] Reglas de `overall_status` (7 reglas del contrato) — con tests
- [x] Reglas de `server.status` (5 reglas del contrato) — con tests
- [x] Incident open/resolve básico (transición ok↔down/critical)
- [ ] **Incident generator con campos humanos** (title, description, diagnosis, impact_label)
  - [ ] Tabla de mapeo error técnico → campos humanos (ver API_CONTRACT.md)
  - [ ] Diagnóstico contextual: correlacionar señales entre checks
  - [ ] Anti-flapping: warning sostenido >5 min antes de incidente
  - [ ] Cálculo de `duration_human` desde `started_at`
- [ ] Tests de la matriz completa de mapeos de incidente

### 5.10 End-to-end con datos reales

- [x] API devuelve datos reales 4/4 servidores ✅
- [x] Frontend carga datos reales en tablet ✅
- [x] Frontend muestra diseño v2 — **Phase 1 completada 2026-05-13**
- [ ] Validar en Tab A8 con diseño v2 completo

---

## FASE 6 · Producción

### 6.1 Hardening

- [ ] Rate limiting (60 reqs/min por IP)
- [ ] Logs estructurados JSON
- [ ] Backup nightly de SQLite

### 6.2 Observability del NOC

- [ ] Health endpoint robusto (verifica collectors + DB + último check)
- [ ] Self-monitoring: 3 fallos consecutivos → incidente

### 6.3 Documentación operativa

- [ ] `OPERATIONS.md`: cómo redeployar, agregar servicio, rotar llaves
- [ ] `TROUBLESHOOTING.md`: errores comunes y soluciones

---

## FASE 7 (V1.5) · Módulo Docker enriquecido

- [ ] CPU/RAM por container con `docker stats`
- [ ] Detección de containers `unhealthy` y propagación a servicios

---

## FASE 8 (V2) · Drill-down y logs en vivo

- [ ] Vista detallada por servicio (modal)
- [ ] Gráficas históricas 24h
- [ ] WebSocket para logs en streaming
- [ ] DKIM check

---

## FASE 9 (V3) · Acciones protegidas

- [ ] PIN + TOTP para activar modo acciones
- [ ] Endpoints `POST /api/v1/action/*`
- [ ] Push notifications a tablet en alertas críticas

---

## Decisiones tomadas durante la implementación

- **2026-05-12**: Confirmado que SUIG, OIC y Mailcow corren en Docker. Módulo Docker en V1.
- **2026-05-12**: VPS-MyRock tiene 2 cores con load ~1.0 — polling 15s/60s para no saturar.
- **2026-05-12**: Tailscale elegido sobre Cloudflare Access por simplicidad.
- **2026-05-12**: Opción A (SSH desde noc-api, sin agentes) por mínima invasividad.
- **2026-05-13**: **Rediseño operativo del frontend.** El primer prototipo era "estética pura" — uniformidad democrática, métricas sin diagnóstico. Se rediseña para responder 4 preguntas operativas. Ver `DESIGN.md`.
- **2026-05-13**: **API_CONTRACT extendido**: `Incident` ahora incluye `title`, `description`, `diagnosis`, `impact_label`, `duration_human`. El aggregator genera estos campos desde fallos técnicos.
- **2026-05-14**: noc-api corre como root (uid 0) en Docker para leer SSH key en /root/.ssh. V1 aceptable tras Tailscale.
- **2026-05-14**: myrock.com.mx SSL vence 2026-05-29 (~15 días) — **renovar antes de esa fecha**.

---

## Bloqueadores actuales

- [ ] **Incident generator incompleto** — incidentes abiertos no tienen title/description/diagnosis. Bloquea la utilidad real del bloque de incidentes en el frontend v2.
- [x] ~~**Frontend v2 no implementado**~~ — implementado 2026-05-13, desplegado en VPS-MyRock.
- [ ] **myrock.com.mx SSL vence 2026-05-29** — renovar antes del 2026-05-22 (7 días de margen).

---

## Backlog (ideas no priorizadas)

- Integración con WhatsApp vía Evolution API para alertas críticas
- Auto-rotación de llaves SSH del NOC cada 6 meses
- Dashboard para PagoKids: transacciones/min, errores
- Export de incidentes a CSV/PDF
- Modo demo sin datos reales
- Detección automática de cambios en infra (nuevo container, nuevo dominio)
- Mobile-responsive para ver desde celular fuera de oficina
