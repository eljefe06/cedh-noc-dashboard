# CONVENTIONS.md — Convenciones del proyecto

## Idioma

- **Código** (variables, funciones, clases, archivos): inglés
- **Comentarios cortos**: inglés
- **Comentarios largos / docstrings**: español si aclara contexto del dominio CEDH, inglés si es técnica genérica
- **Commits**: inglés siguiendo Conventional Commits
- **Documentación** (`/docs`): español
- **UI**: español
- **Logs**: inglés (más fácil para grep)

## Convenciones Python (backend)

### Estilo

- **Black** para formatting (line length 100)
- **Ruff** para linting
- **mypy** opcional en V2

### Imports

```python
# Stdlib primero
import asyncio
from datetime import datetime, timezone
from pathlib import Path

# Third-party
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Local
from app.config import settings
from app.models import Server, Service
```

### Naming

- `snake_case` para funciones y variables
- `PascalCase` para clases
- `UPPER_SNAKE` para constantes
- Prefijo `_` para privados

### Async

Todo I/O debe ser async:

```python
# Bueno
async def check_http(url: str) -> CheckResult:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    return parse(response)

# Malo
def check_http(url: str) -> CheckResult:
    response = requests.get(url)  # bloquea event loop
    return parse(response)
```

### Type hints

Obligatorios en funciones públicas:

```python
async def get_server_metrics(name: str) -> Server | None:
    ...
```

### Docstrings

Solo en funciones públicas y clases. Estilo simple:

```python
async def check_http(url: str, timeout: float = 5.0) -> CheckResult:
    """Hace GET a la URL y devuelve resultado del check.
    
    Args:
        url: URL completa a checar
        timeout: segundos antes de timeout
    
    Returns:
        CheckResult con status, latency_ms, http_status
    """
```

### Manejo de errores

- `try/except` específicos, no `except Exception` genérico
- Loguear el error antes de re-lanzar
- Errores esperados en collectors no deben tumbar el worker, solo marcar el check como `unknown`

```python
try:
    result = await check_http(url)
except httpx.TimeoutException:
    logger.warning("timeout checking %s", url)
    result = CheckResult(status="down", reason="timeout")
except Exception as e:
    logger.exception("unexpected error checking %s", url)
    result = CheckResult(status="unknown", reason=str(e))
```

## Convenciones HTML/CSS/JS (frontend)

### HTML

- Indentación 2 espacios
- Atributos ordenados: `id` → `class` → `data-*` → resto
- `<button type="button">` siempre explícito
- `aria-label` en elementos interactivos sin texto visible

### CSS

- Variables CSS para todos los colores (ver DESIGN.md)
- `kebab-case` para clases
- BEM cuando agrega claridad, no obligatorio
- Una sola hoja de estilos `main.css`, sin frameworks
- No prefijos de vendor (caniuse para target Android Chrome reciente)

```css
.vps-card { /* bueno */ }
.vps-card__name { /* bueno */ }
.vpsCard { /* malo */ }
.vps_card { /* malo */ }
```

### JavaScript

- ES6+ moderno (target: Chrome 100+ en Android)
- `const` por defecto, `let` cuando muta, `var` nunca
- `async/await` sobre `.then()`
- Sin `console.log` en producción (usar logger silenciable)
- Sin librerías externas en V1 (vanilla puro)
- Módulos ES6 (`import`/`export`)

```javascript
// main.js
import { renderDashboard } from './render.js';
import { fetchStatus } from './api.js';

const POLL_INTERVAL = 5000;

async function tick() {
  try {
    const status = await fetchStatus();
    renderDashboard(status);
  } catch (err) {
    showError(err);
  }
}

setInterval(tick, POLL_INTERVAL);
tick(); // primer fetch inmediato
```

### Naming en JS

- `camelCase` para funciones y variables
- `PascalCase` para clases (si se usan)
- `UPPER_SNAKE` para constantes top-level
- Funciones puras sin side effects cuando sea posible

## Convenciones Git

### Branches

- `main` — siempre deployable
- `feat/<nombre-corto>` — features
- `fix/<nombre-corto>` — bugs
- `docs/<nombre-corto>` — solo docs
- `chore/<nombre-corto>` — mantenimiento

### Commits (Conventional Commits)

```
<type>(<scope>): <subject>

<body opcional>

<footer opcional>
```

**Types**:
- `feat`: nueva feature
- `fix`: bug fix
- `docs`: cambios en docs
- `style`: formatting, sin cambios de código
- `refactor`: cambio de código sin nueva feature ni fix
- `test`: agregar/modificar tests
- `chore`: mantenimiento, configs, dependencies

**Scopes** comunes:
- `api`, `frontend`, `collector`, `ssh`, `docker`, `dns`, `ssl`, `docs`

**Ejemplos**:

```
feat(collector): add SSL expiration check via TLS handshake

fix(frontend): correct sparkline rendering for empty data

docs(architecture): clarify ControlMaster behavior in SSH section

chore(deps): bump fastapi to 0.110.0
```

### Mensajes de commit

- Subject ≤ 72 caracteres
- Imperativo presente: "add" no "added"
- Sin punto final
- Body explica el "por qué", no el "qué"

### Tags

Versiones semánticas: `v0.1.0`, `v0.1.1`, `v1.0.0`

## Convenciones de archivos

### Estructura

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py             # entrypoint FastAPI
│   ├── config.py           # settings via pydantic-settings
│   ├── models.py           # pydantic models del contrato
│   ├── storage.py          # SQLite wrapper
│   ├── collectors/
│   │   ├── __init__.py
│   │   ├── base.py         # interface base
│   │   ├── http.py
│   │   ├── ssh.py
│   │   ├── ssl.py
│   │   ├── dns.py
│   │   └── docker.py
│   ├── routers/
│   │   ├── __init__.py
│   │   └── status.py
│   ├── workers.py          # loop async de checks periódicos
│   └── logging_config.py
├── tests/
│   ├── conftest.py
│   ├── test_collectors/
│   └── test_routers/
├── Dockerfile
└── pyproject.toml
```

### Frontend

```
frontend/
├── index.html
├── css/
│   └── main.css
├── js/
│   ├── main.js
│   ├── api.js
│   ├── render.js
│   ├── sparkline.js
│   └── status-colors.js
├── assets/
│   ├── favicon.svg
│   └── fonts/
│       └── JetBrainsMono-Regular.woff2
├── mock-data/
│   └── status.json
└── nginx.conf
```

### Tests

- 1 archivo de test por módulo
- Naming `test_<modulo>.py`
- Fixtures en `conftest.py` cercano

### Variables de entorno

`.env.example` siempre versionado, `.env` siempre ignorado:

```bash
# .env.example
NOC_API_BEARER_TOKEN=changeme
SSH_KEY_PATH=/root/.ssh/noc_collector_ed25519
SQLITE_DB_PATH=/data/noc.db
LOG_LEVEL=INFO
TAILSCALE_IP=100.x.x.x
```

## Convenciones de testing

### Cuándo escribir tests

- **Siempre**: parsing de salidas de comandos SSH, lógica de cálculo de status, transformaciones JSON
- **A veces**: routers (mock collectors)
- **Casi nunca**: configuraciones, simple I/O

### Estilo

`pytest` con `pytest-asyncio`. Naming `test_<should-do-something>`:

```python
async def test_http_collector_returns_ok_on_200():
    result = await http_collector.check("https://example.com/")
    assert result.status == "ok"

async def test_http_collector_returns_down_on_timeout():
    result = await http_collector.check("https://does-not-exist.local/", timeout=0.1)
    assert result.status == "down"
    assert "timeout" in result.last_error.lower()
```

## Convenciones de logs

### Formato

JSON estructurado, ver SECURITY.md:

```json
{
  "ts": "2026-05-12T20:00:00-07:00",
  "level": "INFO",
  "component": "http_collector",
  "service": "SUIG",
  "status": "ok",
  "latency_ms": 184
}
```

### Niveles

- `DEBUG`: detalle exhaustivo (off en producción)
- `INFO`: cada check ejecutado exitosamente
- `WARNING`: degradación, retry, timeout recuperable
- `ERROR`: check fallido, agente no responde
- `CRITICAL`: aplicación no puede continuar

## Convenciones de configuración

Usar `pydantic-settings` para validar `.env`:

```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    noc_api_bearer_token: str
    ssh_key_path: str = "/root/.ssh/noc_collector_ed25519"
    sqlite_db_path: str = "/data/noc.db"
    log_level: str = "INFO"
    tailscale_ip: str
    
    poll_interval_http: int = 15
    poll_interval_metrics: int = 60
    poll_interval_docker: int = 60
    poll_interval_smtp: int = 60
    poll_interval_backups: int = 300
    poll_interval_deploys: int = 60
    poll_interval_ssl: int = 21600
    poll_interval_dns: int = 3600
    poll_interval_ptr: int = 21600
    
    cache_ttl_seconds: int = 5
    
    class Config:
        env_file = ".env"
        env_prefix = ""

settings = Settings()
```

## Convenciones de versionado

Semver: `MAJOR.MINOR.PATCH`

- `MAJOR`: cambios incompatibles del contrato JSON
- `MINOR`: nuevas features compatibles
- `PATCH`: bug fixes

V1 target: `v1.0.0`. V1.5: `v1.5.0`. V2: `v2.0.0` (porque agrega WebSockets que rompen clientes V1).
