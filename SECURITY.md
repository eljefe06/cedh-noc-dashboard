# SECURITY.md — Threat model y prácticas de seguridad

## Threat model resumido

### Lo que estamos protegiendo

1. **Acceso a infraestructura institucional** vía las llaves SSH del NOC
2. **Información operativa interna** mostrada en el dashboard (qué corre dónde, qué está caído)
3. **Disponibilidad del NOC mismo** (no debe ser DoSeable)
4. **Integridad de los servidores monitoreados** (el NOC nunca debe degradarlos)

### De qué nos protegemos

| Amenaza | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Atacante externo escaneando IP pública | Alta | Bajo si Tailscale | Tailscale, no exponer puertos |
| Tablet robada | Baja | Medio | Login Tailscale, no guardar tokens |
| Llave SSH del NOC comprometida | Baja | Alto | Llave dedicada, restricciones `command=`, rotación periódica |
| API del NOC con bug que ejecute código en VPS monitoreados | Baja | Crítico | Solo comandos read-only via SSH, validación estricta de inputs |
| Exposición accidental del dashboard a internet | Media | Medio | Firewall UFW por defecto cerrado, escucha solo en IP Tailscale |
| Secrets en repos públicos | Alta sin disciplina | Alto | `.env` en `.gitignore`, secrets manager, revisión pre-commit |
| Logs con info sensible | Media | Medio | Log redaction, no loguear tokens ni PII |

### De qué NO nos protegemos en V1

- Atacante con acceso físico a VPS-MyRock (es un riesgo aceptado)
- Compromiso del proveedor (Hetzner)
- Side-channels de timing entre containers en VPS-MyRock
- Phishing al usuario (Jorge)

## Tailscale

### Configuración

Cuenta personal de Jorge (Google o GitHub auth). Plan free es suficiente (hasta 100 dispositivos).

**Dispositivos en el tailnet**:
- `vps-myrock` (host del NOC)
- `tab-a8` (cliente)
- `laptop-jorge` (acceso administrativo)
- *(opcional)* `vps-suig`, `vps-oic`, `vps-mail` — recomendado pero no requerido en V1

### ACL recomendada

```hujson
{
  "groups": {
    "group:noc-admin": ["jorge@example.com"],
    "group:noc-readonly": ["jorge@example.com"]
  },
  "tagOwners": {
    "tag:vps-myrock": ["group:noc-admin"],
    "tag:vps-monitored": ["group:noc-admin"],
    "tag:tablet": ["group:noc-readonly"]
  },
  "acls": [
    // tablet solo puede ver el NOC
    {
      "action": "accept",
      "src": ["tag:tablet"],
      "dst": ["tag:vps-myrock:80,8000"]
    },
    // VPS-MyRock puede hablar SSH a monitoreados (si están en tailnet)
    {
      "action": "accept",
      "src": ["tag:vps-myrock"],
      "dst": ["tag:vps-monitored:22"]
    },
    // laptop tiene acceso total
    {
      "action": "accept",
      "src": ["group:noc-admin"],
      "dst": ["*:*"]
    }
  ]
}
```

### MagicDNS

Activar para usar `vps-myrock.tailnet.ts.net` en lugar de IPs. Más legible.

## SSH del NOC

### Llave dedicada (NO la personal)

Generar en VPS-MyRock:

```bash
ssh-keygen -t ed25519 \
  -C "noc-collector@vps-myrock-$(date +%Y%m)" \
  -f ~/.ssh/noc_collector_ed25519 \
  -N ""    # sin passphrase porque corre automatizado
```

> **Importante**: la passphrase vacía es necesaria para que el daemon pueda usarla sin intervención humana. Esto se compensa con **restricciones de comando** en los servidores destino.

### Instalación de la llave pública en cada VPS monitoreado

En `/root/.ssh/authorized_keys` de cada VPS (suig-vps, vps-oic, cedh-mail):

```
restrict,command="/usr/local/bin/noc-readonly-shell" ssh-ed25519 AAAA... noc-collector@vps-myrock-202605
```

El script `noc-readonly-shell` solo permite ejecutar comandos pre-aprobados:

```bash
#!/bin/bash
# /usr/local/bin/noc-readonly-shell
# Filtro de comandos permitidos para el NOC

set -euo pipefail

ALLOWED_COMMANDS=(
    "uptime"
    "cat /proc/loadavg"
    "free -m"
    "df -h /"
    "docker ps --format json"
    "docker ps -a --format json"
    "docker stats --no-stream --format json"
    "docker version --format '{{.Server.Version}}'"
    "ss -tlnp"
    "systemctl is-active nginx"
    "systemctl is-active apache2"
    "ls -la /var/backups/ | tail -20"
    "git -C /opt/* log -1 --format='%h %ai %s'"
)

CMD="$SSH_ORIGINAL_COMMAND"

# Validar contra whitelist
for allowed in "${ALLOWED_COMMANDS[@]}"; do
    if [[ "$CMD" == "$allowed"* ]]; then
        exec /bin/bash -c "$CMD"
    fi
done

echo "ERROR: Command not allowed: $CMD" >&2
exit 1
```

Esto significa que **aunque la llave del NOC sea comprometida**, solo puede ejecutar comandos read-only definidos.

### SSH config en VPS-MyRock

`~/.ssh/config`:

```
Host suig-vps
    HostName <ip-publica-suig>
    User root
    IdentityFile ~/.ssh/noc_collector_ed25519
    IdentitiesOnly yes
    ControlMaster auto
    ControlPath ~/.ssh/cm-%r@%h:%p
    ControlPersist 10m
    ServerAliveInterval 30
    StrictHostKeyChecking yes
    UserKnownHostsFile ~/.ssh/known_hosts_noc

Host vps-oic
    HostName <ip-publica-oic>
    User root
    IdentityFile ~/.ssh/noc_collector_ed25519
    IdentitiesOnly yes
    ControlMaster auto
    ControlPath ~/.ssh/cm-%r@%h:%p
    ControlPersist 10m
    ServerAliveInterval 30
    StrictHostKeyChecking yes
    UserKnownHostsFile ~/.ssh/known_hosts_noc

Host cedh-mail
    HostName <ip-publica-mail>
    User root
    IdentityFile ~/.ssh/noc_collector_ed25519
    IdentitiesOnly yes
    ControlMaster auto
    ControlPath ~/.ssh/cm-%r@%h:%p
    ControlPersist 10m
    ServerAliveInterval 30
    StrictHostKeyChecking yes
    UserKnownHostsFile ~/.ssh/known_hosts_noc
```

`StrictHostKeyChecking yes` previene MITM. Primera conexión requiere confirmación manual.

### Rotación de llaves

Schedule recomendado: **cada 6 meses**.

Procedimiento:
1. Generar nueva llave en VPS-MyRock con sufijo nuevo en comentario
2. Instalar nueva pública en `authorized_keys` de los 3 destinos (adicional, no reemplazo)
3. Cambiar `IdentityFile` en SSH config local
4. Probar conexión
5. Remover llave vieja de `authorized_keys`
6. Borrar llave privada vieja

## Secrets

### Donde NO van

- ❌ Repositorio (ni público ni privado)
- ❌ Mensajes de commit
- ❌ Logs de la aplicación
- ❌ Respuestas de la API
- ❌ Variables de entorno expuestas en `docker inspect`

### Donde SÍ van

V1 mínimo:
- `.env` en VPS-MyRock, fuera del repo, permisos `0600`, propietario `root`
- `.gitignore` con `.env`, `*.key`, `*.pem`
- Llaves SSH en `~/.ssh/` con `0600`

V2+ recomendado:
- Vault, Doppler, AWS Secrets Manager, o 1Password CLI

### Secrets esperados

```env
# .env
NOC_API_BEARER_TOKEN=<token-largo-aleatorio>
TAILSCALE_AUTHKEY=<solo-si-se-automatiza>
SSH_KEY_PATH=/root/.ssh/noc_collector_ed25519
SQLITE_DB_PATH=/data/noc.db
LOG_LEVEL=INFO
```

Generar el token con:

```bash
openssl rand -base64 48
```

## Firewall

### VPS-MyRock

UFW configurado con default deny inbound:

```bash
ufw default deny incoming
ufw default allow outgoing

# SSH público (mantener acceso de Jorge)
ufw allow 22/tcp

# HTTP/HTTPS para los proyectos existentes (myrock, pagokids, etc)
ufw allow 80/tcp
ufw allow 443/tcp

# Tailscale (no necesita regla explícita, pero documentado)
# Tailscale crea su propia interfaz

# NOC dashboard NO se expone via UFW
# Escucha solo en la interfaz tailscale0

ufw enable
```

### Hardening del puerto del NOC

FastAPI debe escuchar **solo en la interfaz Tailscale**:

```python
# En uvicorn config:
host = "100.x.x.x"  # IP Tailscale específica, no "0.0.0.0"
```

O bien, en Docker Compose:

```yaml
services:
  noc-api:
    ports:
      - "100.x.x.x:8000:8000"  # bind explícito a IP Tailscale
```

Esto garantiza que aunque alguien escanee la IP pública, no encontrará el puerto del NOC.

## Logging

### Qué SÍ loguear

- Cada check ejecutado (servicio, timestamp, resultado)
- Transiciones de estado (ok → warning → critical)
- Errores de conexión a VPS monitoreados
- Requests a la API (método, path, status, latencia)

### Qué NO loguear

- Tokens, llaves, passwords
- Contenido completo de respuestas HTTP (solo metadata)
- Comandos SSH ejecutados con sus argumentos sensibles
- PII de la operación CEDH (nombres de funcionarios, folios específicos)

### Formato

JSON estructurado para fácil parsing:

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

### Retención

- En disco: 7 días con rotación diaria
- En SQLite (eventos importantes): 90 días

## Auditoría

### Eventos a registrar en `events` table

- Inicio/fin de cada check ciclo
- Cambio de estado de cualquier servicio
- Conexión SSH a cada VPS (timestamp, éxito/fallo)
- Acceso al dashboard desde la tablet (V2 con auth)

### Sin auditoría

V1 no tiene multi-user, no requiere audit log de acciones porque no hay acciones.

## Actualizaciones de seguridad

### Sistema operativo

```bash
unattended-upgrades  # ya instalado por defecto en Ubuntu
```

Configurado para aplicar **security updates automáticamente**.

### Dependencias Python

```bash
pip-audit  # ejecutar mensualmente
```

Si hay CVE crítico en FastAPI o sus dependencias, actualizar y redeployar.

### Imagen Docker base

Pin a versión específica de Python:

```dockerfile
FROM python:3.11.10-slim-bookworm
```

Rebuild mensual aunque no haya cambios, para tomar parches de seguridad de la imagen base.

## Backup de la propia data del NOC

Backup nightly de `/data/noc.db` a:

1. Otro directorio en VPS-MyRock (snapshot rápido)
2. (V2) Storage externo encriptado

```bash
# Cron diario 4 AM
0 4 * * * /usr/local/bin/noc-backup.sh
```

```bash
#!/bin/bash
# /usr/local/bin/noc-backup.sh
set -euo pipefail

BACKUP_DIR=/var/backups/noc
TODAY=$(date +%Y%m%d)
mkdir -p "$BACKUP_DIR"

sqlite3 /data/noc.db ".backup '$BACKUP_DIR/noc_$TODAY.db'"
gzip "$BACKUP_DIR/noc_$TODAY.db"

# Retener 14 días
find "$BACKUP_DIR" -name "noc_*.db.gz" -mtime +14 -delete
```

## Checklist de seguridad pre-producción

Antes de marcar V1 como "production ready", verificar:

- [ ] Tailscale corriendo en VPS-MyRock y Tab A8
- [ ] Firewall UFW activo, NOC no expuesto en IP pública
- [ ] SSH NOC con llave dedicada (no la personal)
- [ ] `noc-readonly-shell` instalado en los 3 VPS monitoreados
- [ ] `.env` con permisos 0600, fuera del repo
- [ ] `.gitignore` cubre `.env`, `*.key`, `*.pem`, `noc.db`
- [ ] FastAPI con `docs_url=None, redoc_url=None, openapi_url=None`
- [ ] HTTPS no necesario internamente (Tailscale ya encripta) pero **documentado** el porqué
- [ ] `unattended-upgrades` activo en VPS-MyRock
- [ ] Backup nightly de SQLite funcionando
- [ ] Logs no contienen secretos (revisar manualmente primera semana)
