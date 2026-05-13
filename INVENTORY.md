# INVENTORY.md — Inventario maestro de infraestructura

> Estado: **parcialmente verificado**. Solo VPS-MyRock fue discovery-eado a fondo. Los demás están con datos por confirmar.
> Última actualización: 2026-05-12

---

## VPS-1 · VPS-MyRock (alias OpenClaw)

> ✅ Discovery completo realizado el 2026-05-12

| Campo | Valor |
|---|---|
| Hostname real | `srv1386238` |
| Alias humano | `openclaw` / `vps-myrock` |
| Proveedor | Hetzner |
| Región | (por confirmar — probablemente nbg1 o fsn1) |
| OS | Ubuntu 24.04.4 LTS |
| Kernel | (ver discovery JSON) |
| Specs reales | 2 vCPU / 7940 MB RAM / 96 GB disco |
| RAM en uso | 2858 / 7940 MB (36%) |
| Disco en uso | 54 GB / 96 GB (56%) |
| Load avg | 1.07 / 1.20 / 1.20 |
| Docker version | v29.3.0 |
| Containers | 10/10 running |
| PM2 procesos | 5 |
| SSL certs | 14 dominios en Let's Encrypt |
| IP pública | (por completar) |
| IP Tailscale | `100.104.244.83` |
| Rol en NOC | **Hosta API central + frontend + checker engine** |

### Proyectos Docker Compose detectados

| Proyecto | Notas |
|---|---|
| `evolution-api` | Evolution API v1 — ¿candidato a deprecación? |
| `evolution-api-v2` | Evolution API v2 — versión actual |
| `infra` | Probablemente nginx-proxy + certbot |
| `myrock-stack` | Apps de MyRock |
| `n8n` | Automatizaciones |
| `naibi-stack` | Naibi Concept Store |

> **Pendiente**: mapear container → proyecto compose viendo el JSON completo del discovery.

### Servicios HTTP que corren aquí

- [ ] (por completar) MyRock web — dominio: ?
- [ ] (por completar) PagoKids — dominio: pagokids.com.mx
- [ ] (por completar) ChatRock — dominio: ?
- [ ] (por completar) n8n — dominio: ?
- [ ] (por completar) Naibi Concept Store — dominio: ?
- [ ] (por completar) Evolution API endpoints

### Procesos PM2 (5 detectados)

> **Pendiente**: identificar nombres y propósito. Posibilidad de que algunos ya estén migrados a Docker y sean residuales.

---

## VPS-2 · VPS-SUIG

> ⏳ Discovery pendiente

| Campo | Valor |
|---|---|
| Hostname | `___` |
| Proveedor | (por confirmar — probablemente Hetzner) |
| Región | (por confirmar) |
| OS | (por confirmar) |
| Specs | ___ vCPU / ___ GB RAM / ___ GB disco |
| Docker | Sí (confirmado por Jorge) |
| IP pública | `___.___.___.___` |
| IP Tailscale | (pendiente) |
| Rol en NOC | Monitoreado por SSH |

### Servicios que corren aquí

- [ ] **SUIG** (Sistema Único de Información para la Gestión de Quejas) — Docker
- [ ] **cedhsinaloa.org.mx** — WordPress (¿confirmar si vive aquí?)
- [ ] **Mesa de Control** (módulo SUIG)
- [ ] **Buzón Electrónico** — `buzon.cedhsinaloa.org.mx`
- [ ] **cedhs.xyz** — acortador URL
- [ ] MariaDB / MySQL (motor DB de SUIG)

### Bloqueadores antes de monitoreo

- [ ] Confirmar hostname e IP pública
- [ ] Confirmar dominio público de SUIG (probablemente `suig.cedhsinaloa.org.mx`)
- [ ] Confirmar si cedhsinaloa.org.mx vive aquí o en otro lado
- [ ] Asegurar SSH desde VPS-MyRock funciona

---

## VPS-3 · VPS-OIC

> ⏳ Discovery pendiente

| Campo | Valor |
|---|---|
| Hostname | `___` |
| Proveedor | (por confirmar) |
| Región | (por confirmar) |
| OS | (por confirmar) |
| Specs | ___ vCPU / ___ GB RAM / ___ GB disco |
| Docker | Sí (confirmado por Jorge) |
| IP pública | `___.___.___.___` |
| IP Tailscale | (pendiente) |
| Rol en NOC | Monitoreado por SSH |

### Servicios que corren aquí

- [ ] **Declaraciones** patrimoniales (integrado con PDN) — dominio: ?
- [ ] **Denuncias** — dominio: ?
- [ ] **CEDH-SIER** (Sistema de Entrega-Recepción) / SER-CEDH — dominio: ?
- [ ] Base de datos (¿Postgres? ¿MySQL? — por confirmar)

### Bloqueadores antes de monitoreo

- [ ] Confirmar hostname, proveedor, IP
- [ ] Confirmar dominios públicos de los 3 sistemas
- [ ] Confirmar motor DB
- [ ] Asegurar SSH desde VPS-MyRock funciona

---

## VPS-4 · VPS-Mail (cedh-mail)

> ⏳ Discovery pendiente

| Campo | Valor |
|---|---|
| Hostname | `___` |
| Proveedor | Contabo |
| Región | EU |
| OS | (por confirmar — Debian o Ubuntu) |
| Specs | ___ vCPU / ___ GB RAM / ___ GB disco |
| Docker | Sí (Mailcow ES Docker) |
| Dominio principal | `mail.cedhsinaloa.org.mx` |
| IP pública | `___.___.___.___` |
| IP Tailscale | (pendiente) |
| Rol en NOC | Monitoreado por SSH — **frágil, no tocar mucho** |

### Servicios que corren aquí

Stack Mailcow completo (todos containers Docker):
- [ ] **Postfix** (SMTP) — puerto 25, 587
- [ ] **Dovecot** (IMAP) — puerto 993
- [ ] **Rspamd** (anti-spam)
- [ ] **SOGo** (webmail)
- [ ] **Nginx interno de Mailcow**
- [ ] **MySQL/MariaDB interno**
- [ ] **Redis interno**
- [ ] **ClamAV**
- [ ] **Mailcow admin web**

### Bloqueadores antes de monitoreo

- [ ] Confirmar hostname, IP
- [ ] Confirmar que DNS records (MX, SPF, DMARC) están bien configurados — Jorge tiene pendiente esto
- [ ] PTR de IP pública apunta a `mail.cedhsinaloa.org.mx`
- [ ] Asegurar SSH desde VPS-MyRock funciona

---

## Servicios HTTP monitoreados (tabla maestra)

> Niveles de criticidad:
> - `high`: caída impacta operación CEDH directamente
> - `medium`: caída es molesta pero no operacional
> - `low`: experimental o personal

| Servicio | URL para check | Servidor | Criticidad | Estado |
|---|---|---|---|---|
| cedhsinaloa.org.mx | `https://cedhsinaloa.org.mx/` | suig-vps (?) | high | pendiente |
| SUIG | `https://suig.cedhsinaloa.org.mx/` | suig-vps | high | pendiente |
| Buzón Electrónico | `https://buzon.cedhsinaloa.org.mx/` | suig-vps | high | pendiente |
| SER-CEDH | `https://___/` | vps-oic | high | pendiente |
| Declaraciones | `https://___/` | vps-oic | high | pendiente |
| Denuncias | `https://___/` | vps-oic | high | pendiente |
| Mailcow SOGo | `https://mail.cedhsinaloa.org.mx/SOGo/` | cedh-mail | high | pendiente |
| Mailcow admin | `https://mail.cedhsinaloa.org.mx/` | cedh-mail | medium | pendiente |
| cedhs.xyz | `https://cedhs.xyz/` | suig-vps | medium | pendiente |
| MyRock | `https://myrock.com.mx/` | vps-myrock | medium | pendiente |
| PagoKids | `https://pagokids.com.mx/` | vps-myrock | high | pendiente |
| ChatRock | `https://___/` | vps-myrock | low | pendiente |
| Naibi Concept Store | `https://___/` | vps-myrock | low | pendiente |

---

## DNS y correo (checks V1)

| Check | Tipo | Dominio/Target | Esperado | Criticidad |
|---|---|---|---|---|
| MX existe | DNS | `cedhsinaloa.org.mx` MX | `mail.cedhsinaloa.org.mx` | high |
| SPF existe | DNS | `cedhsinaloa.org.mx` TXT | contiene `v=spf1` | high |
| DMARC existe | DNS | `_dmarc.cedhsinaloa.org.mx` TXT | contiene `v=DMARC1` | high |
| Mail A record | DNS | `mail.cedhsinaloa.org.mx` A | IP pública de cedh-mail | high |
| PTR reverse | rDNS | IP pública de cedh-mail | `mail.cedhsinaloa.org.mx` | high |
| SMTP 587 | TCP+STARTTLS | `mail.cedhsinaloa.org.mx:587` | conecta + TLS | high |
| IMAP 993 | TCP+TLS | `mail.cedhsinaloa.org.mx:993` | conecta | high |

---

## Certificados SSL a monitorear

> Source of truth: check TLS externo desde noc-api hacia el dominio público.

| Dominio | Servidor donde vive el cert | Threshold |
|---|---|---|
| cedhsinaloa.org.mx | suig-vps | <30d warn, <7d crit |
| suig.cedhsinaloa.org.mx | suig-vps | igual |
| buzon.cedhsinaloa.org.mx | suig-vps | igual |
| mail.cedhsinaloa.org.mx | cedh-mail | igual |
| cedhs.xyz | suig-vps | igual |
| (dominios OIC) | vps-oic | igual |
| myrock.com.mx | vps-myrock | igual |
| pagokids.com.mx | vps-myrock | igual |
| (otros 14 detectados en discovery) | vps-myrock | igual |

---

## Umbrales de alerta

**Estados**: `ok` · `warning` · `critical` · `down`
`down` se reserva solo para servicios que no responden. Métricas de recursos usan `critical`.

| Métrica | OK | WARNING | CRITICAL | DOWN | Source |
|---|---|---|---|---|---|
| CPU | <70% | 70-90% | >90% sostenido 5min | — | SSH |
| RAM | <75% | 75-90% | >90% | — | SSH |
| Disco | <80% | 80-90% | >90% | — | SSH |
| Load 1m | <cores | cores-2×cores | >2×cores | — | SSH |
| HTTP latency | <500ms | 500-2000ms | >2000ms | timeout | noc-api |
| HTTP status | 200-299 | 300-399 | 4xx | 5xx / no conecta | noc-api |
| SSL días | >30d | 7-30d | <7d | inválido | noc-api |
| Backup age | <30h | 30-72h | >72h | — | SSH |
| Docker container | running healthy | unhealthy | exited (no esperado) | — | SSH |
| DNS record | resuelve | inconsistente | falta/inválido | no resuelve | noc-api |

---

## Pendientes para resolver

- [ ] Discovery v2 corriendo en VPS-SUIG
- [ ] Discovery v2 corriendo en VPS-OIC
- [ ] Discovery v2 corriendo en VPS-Mail
- [ ] Confirmar dónde vive cedhsinaloa.org.mx
- [ ] Confirmar dominios OIC
- [ ] Crear cuenta Tailscale e instalar en VPS-MyRock + Tab A8
- [ ] Crear llave SSH dedicada `noc_collector_ed25519` en VPS-MyRock
- [ ] Instalar llave pública en los otros 3 VPS
- [ ] Probar SSH desde VPS-MyRock con la llave dedicada
- [ ] Limpiar/identificar los 5 procesos PM2 huérfanos en VPS-MyRock
- [ ] Decidir si Evolution API v1 ya se puede apagar (queda v2)
