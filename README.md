# CEDH NOC Dashboard

> Centro de operaciones de red (NOC) personal para la infraestructura de Jorge Yanagui — Jefe de la Unidad de Diseño Institucional y Sistemas (UDIyS) de la Comisión Estatal de los Derechos Humanos de Sinaloa.

Dashboard cyberpunk de monitoreo de 4 VPS y los servicios que corren en ellos. Diseñado para verse en una Samsung Galaxy Tab A8 en modo kiosko, pegada al monitor principal.

## Lectura obligatoria antes de tocar código

Lee estos archivos **en este orden** antes de empezar:

1. [`docs/PROJECT.md`](docs/PROJECT.md) — Qué es, para quién, por qué existe
2. [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — Cómo encajan las piezas
3. [`docs/INVENTORY.md`](docs/INVENTORY.md) — Los 4 servidores y qué corre en cada uno
4. [`docs/API_CONTRACT.md`](docs/API_CONTRACT.md) — Contrato JSON (cerrado, no modificar sin versionar)
5. [`docs/DESIGN.md`](docs/DESIGN.md) — Estética cyberpunk dark y reglas visuales
6. [`docs/SECURITY.md`](docs/SECURITY.md) — Tailscale, secrets, threat model
7. [`docs/CONVENTIONS.md`](docs/CONVENTIONS.md) — Cómo se escribe código aquí
8. [`docs/GLOSSARY.md`](docs/GLOSSARY.md) — Términos del dominio CEDH
9. [`docs/TASKS.md`](docs/TASKS.md) — Lista de tareas con checkboxes
10. [`CLAUDE.md`](CLAUDE.md) — Instrucciones específicas para Claude Code

## Stack

- **Backend API**: FastAPI (Python 3.11+)
- **Frontend**: HTML + CSS + vanilla JS + SVG sparklines
- **Persistencia**: SQLite
- **Red interna**: Tailscale (no internet público)
- **Cliente**: PWA en Fully Kiosk Browser, Samsung Tab A8
- **Deploy**: Docker Compose

## Estructura del repo

```
cedh-noc-dashboard/
├── README.md                       Este archivo
├── CLAUDE.md                       Instrucciones para Claude Code
├── docs/                           Documentación del proyecto
│   ├── PROJECT.md
│   ├── ARCHITECTURE.md
│   ├── INVENTORY.md
│   ├── API_CONTRACT.md
│   ├── DESIGN.md
│   ├── SECURITY.md
│   ├── CONVENTIONS.md
│   ├── GLOSSARY.md
│   └── TASKS.md
├── backend/                        FastAPI API central
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── models.py
│   │   ├── collectors/             Cada tipo de check
│   │   ├── routers/
│   │   └── storage.py
│   ├── tests/
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/                       HTML + CSS + JS vanilla
│   ├── index.html
│   ├── css/
│   ├── js/
│   ├── assets/
│   └── mock-data/
├── scripts/                        Discovery, deploy, utilidades
│   ├── discovery-v2.sh
│   └── deploy.sh
├── docker-compose.yml
└── .env.example
```

## Estado del proyecto

Ver [`docs/TASKS.md`](docs/TASKS.md) para checklist completo.

**Fase actual**: V0 — Setup inicial y frontend mock.

## Para Jorge (el operador humano)

Cuando vuelvas a este proyecto después de un tiempo, lee [`docs/PROJECT.md`](docs/PROJECT.md) primero para recordar qué onda. Luego mira [`docs/TASKS.md`](docs/TASKS.md) para ver dónde te quedaste.

Si Claude Code lo está manejando, dile literalmente: *"Lee docs/PROJECT.md, docs/TASKS.md, y CLAUDE.md, luego continúa donde nos quedamos"*. Eso es suficiente.
