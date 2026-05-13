# PROJECT.md — Qué es esto y por qué existe

## El proyecto en una frase

Dashboard NOC (Network Operations Center) personal para 4 VPS, visualizado en una Samsung Tab A8 en modo kiosko al lado del monitor principal, con estética cyberpunk dark.

## El operador

**Jorge Yanagui Kuroda** — 36 años, vive en Culiacán, Sinaloa.

**Rol institucional**: Jefe de la Unidad de Diseño Institucional y Sistemas (UDIyS) en la Comisión Estatal de los Derechos Humanos de Sinaloa (CEDH Sinaloa).

**Rol freelance**: Fundador de MyRock (agencia digital) y co-fundador de PagoKids (NFC payments).

**Nivel técnico**: alto. Desarrolla activamente en PHP/Laravel, Python, Node.js, FastAPI, Docker. Usa Claude Code como capa de ejecución. Self-hosting en Hetzner y Contabo. Familiar con SSH, nginx, Docker Compose, n8n, Evolution API, sistemas distribuidos básicos.

## Por qué existe este dashboard

Jorge maneja 4 servidores con servicios críticos institucionales y comerciales:

1. **VPS-MyRock** (srv1386238 / OpenClaw) — Sus proyectos personales: MyRock, PagoKids, ChatRock, n8n, Evolution API, Naibi-stack
2. **VPS-SUIG** — Sistemas institucionales CEDH: SUIG (gestión de quejas), cedhsinaloa.org.mx
3. **VPS-OIC** — Sistemas del Órgano Interno de Control: Declaraciones patrimoniales, Denuncias, SER-CEDH (entrega-recepción)
4. **VPS-Mail** — Servidor de correo institucional Mailcow (mail.cedhsinaloa.org.mx)

**El problema operativo real**:
- Cuando algo se cae, se entera por alguien quejándose
- No tiene visibilidad consolidada del estado
- Cambios al sitio web a veces no se ven por caché
- Certificados SSL pueden vencer sin aviso (le pasó casi con Mailcow)
- No sabe rápidamente qué containers están vivos en cada VPS

**El problema afectivo**: Jorge quiere una **pantalla de control física** que pueda voltear a ver desde el escritorio, no otra pestaña más del navegador. Por eso la tablet, por eso la estética cyberpunk — para que se sienta como **su cabina de mando**, no como un dashboard institucional aburrido.

## Para quién NO es este proyecto

- **No** es para el área sustantiva del CEDH (no muestra quejas, firmas, declaraciones).
- **No** es para el Presidente del CEDH ni para Sergio Hernández (Jefe de Sistemas).
- **No** es un status page público de cedhsinaloa.org.mx.
- **No** reemplaza Grafana/Prometheus para análisis histórico.

Es **explícitamente personal** y técnico. Si más adelante se comparte, será con una versión separada y autorizada.

## Decisiones de diseño cerradas

### Arquitectura
- **Opción A "Mínimo invasivo"**: solo el VPS de MyRock tiene cosas nuevas; los otros 3 no se tocan.
- Acceso desde la API central a los otros VPS vía **SSH con llaves** (no agentes locales en v1).
- **Tailscale** para que el dashboard sea invisible en internet público.
- **SQLite** suficiente para v1 (histórico de incidentes, cache de checks).

### Visualización
- **Cyberpunk dark**: fondo púrpura casi negro, neones magenta/cyan/lima eléctrico/naranja warning.
- **Landscape 1280x800** efectivo en la Tab A8.
- **Solo lectura en V1**. Sin botones de acción (evita resets accidentales por toques en la tablet).
- **Tipografía monoespaciada** estilo terminal.
- Glow real con `box-shadow` y `text-shadow`, no gradientes pastel.

### Operación
- **Polling intervals escalonados** según tipo de check (HTTP 15s, métricas 60s, SSL 6h, DNS 1h).
- **Cache de 5s en la API central**, tablet pollea cada 5s → respuesta inmediata.
- **Logs y deploys** se leen, pero no se mostrarán en streaming hasta V2.

## Decisiones explícitamente diferidas

| Feature | Por qué se difiere | A qué versión |
|---|---|---|
| Logs en streaming | Requiere WebSocket que complica V1 | V2 |
| Gráficas históricas 24h | Requiere store de tiempo-serie | V2 |
| Acciones (restart, purge, redeploy) | Riesgo accidental con tablet táctil | V3 con PIN+TOTP |
| Agentes locales en VPS monitoreados | Política institucional + invasividad | V1.5 si hace falta |
| DKIM check | Complicado por subdomain selector | V2 |
| Status page público | Mezcla audiencias | Otro proyecto separado |
| Push notifications a la tablet | Requiere FCM o similar | V3 |
| Soporte multi-usuario | Solo Jorge en V1 | V3 si aplica |

## Filosofía de implementación

**Reglas duras**:
1. **Si no está documentado, no se implementa.** Cambios fuera de scope se agregan a TASKS.md primero, se discuten, y si se aprueban, se implementan.
2. **El contrato JSON es ley.** Cambios mayores requieren versionar a `/api/v2/`.
3. **La tablet es read-only en V1.** Sin excepción.
4. **No invasividad.** Si un cambio requiere instalar algo en suig-vps, vps-oic o cedh-mail, hay que justificarlo.
5. **Secrets jamás en código.** Variables de entorno o secrets manager.
6. **Cada feature se prueba con datos mock antes de conectar realidad.**

**Reglas blandas**:
1. Prefiere claridad a inteligencia. Código que se entiende a 6 meses > código clever.
2. Comentarios en español donde el contexto lo amerite. Código y commits en inglés.
3. No agregar dependencias gratuitas. Cada nueva librería es deuda futura.
4. Mejor un sparkline SVG hecho a mano que importar Chart.js en V1.

## Filosofía de continuidad

Este proyecto se construye con **Claude Code** como agente de ejecución. La documentación está escrita para que Claude pueda retomar el trabajo en cualquier punto sin que Jorge tenga que re-explicar contexto.

**Si Claude Code abre este repo por primera vez**:
1. Lee README.md, PROJECT.md, ARCHITECTURE.md, TASKS.md, CLAUDE.md
2. Identifica la última tarea con `[~]` (en progreso) o la primera con `[ ]` (pendiente)
3. Continúa desde ahí

**Si Jorge regresa después de tiempo**:
1. Lee este archivo para recordar el "porqué"
2. Revisa TASKS.md para ver dónde se quedó
3. Si va a delegar a Claude Code, le dice: *"continúa donde nos quedamos en TASKS.md"*

## Cómo este proyecto encaja con la vida de Jorge

Jorge tiene varios proyectos paralelos (BetTracker, Mailcow migration, PagoKids, MyRock, Naibi Concept Store, Spanish nationality research, music production, etc.). Este NOC dashboard:

- **No es la prioridad #1** — es soporte operativo
- **No debe absorber tiempo desproporcionado** — V1 en 1-2 semanas máx
- **Debe ser disfrutable de construir** — por eso la estética cyberpunk, por eso es personal
- **Debe ser autosuficiente cuando esté listo** — una vez en producción, mantiene <30 min/mes
