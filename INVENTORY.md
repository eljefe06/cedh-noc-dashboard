# INVENTORY.md — Inventario maestro de infraestructura

> Estado: **SSH verificado en los 4 servidores**. Specs reales obtenidos. Discovery completo pendiente para SUIG/OIC/Mail.
> Última actualización: 2026-05-13

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

> ✅ SSH verificado 2026-05-13 — specs reales obtenidos

| Campo | Valor |
|---|---|
| Hostname real | `srv1482895` |
| Proveedor | Hetzner |
| Región | (por confirmar) |
| OS | Ubuntu 22.04.5 LTS |
| Specs reales | 4 vCPU / 15988 MB RAM (~16 GB) / 194 GB disco |
| RAM en uso | 1748 / 15988 MB (11%) |
| Disco en uso | 42 GB / 194 GB (22%) |
| Load avg | 0.36 / 0.28 / 0.24 |
| Docker | v29.3.0 |
| IP pública | `187.124.152.86` |
| IP Tailscale | (pendiente — no instalado aún) |
| SSH user NOC | `root` |
| Rol en NOC | Monitoreado por SSH desde VPS-MyRock |

### Docker Compose projects

| Proyecto | Containers | Notas |
|---|---|---|
| `suig-cedh` | suig-local-web (Apache), suig-local-db (MariaDB 11.5) | App principal + proxy inverso para todo |
| `cedh-sinaloa` | cedh-sinaloa-web (WordPress php8.1), cedh-sinaloa-db (MariaDB 10.11) | Sitio institucional |
| `evolution-api` | evolution-api (v1.8.2), redis, mongo, postgres | Solo en 127.0.0.1:8080 — interno |

### Dominios verificados (Apache vhosts)

| Dominio | Tipo | URL check | Criticidad |
|---|---|---|---|
| `cedhsinaloa.org.mx` | WordPress (proxy → cedh-sinaloa-web) | `https://cedhsinaloa.org.mx/` | high |
| `www.cedhsinaloa.org.mx` | alias de lo anterior | — | — |
| `suig.cedhsinaloa.org.mx` | SUIG app PHP/Apache | `https://suig.cedhsinaloa.org.mx/` | high |
| `buzon.cedhsinaloa.org.mx` | Buzón Electrónico (mismo código SUIG, distinto vhost) | `https://buzon.cedhsinaloa.org.mx/` | high |
| `suigcedhsinaloa.org.mx` | Dominio legacy (vhost suig-ssl.conf) | `https://suigcedhsinaloa.org.mx/` | low |

### Certificados SSL

| Cert | Dominios cubiertos | Expira | Días restantes |
|---|---|---|---|
| cedhsinaloa.org.mx-0001 | cedhsinaloa.org.mx, www. | 2026-08-08 | ~87d ✅ |
| Pendiente verificar | suig., buzon. subdomains | — | — |

### Bloqueadores antes de monitoreo

- [x] Confirmar hostname e IP pública → srv1482895 / 187.124.152.86
- [x] Asegurar SSH desde VPS-MyRock funciona ✅
- [x] Confirmar dominio SUIG → `suig.cedhsinaloa.org.mx` ✅
- [x] Confirmar si cedhsinaloa.org.mx vive aquí → Sí, WordPress en proxy ✅
- [ ] Verificar SSL de suig. y buzon. subdomains
- [ ] Confirmar si cedhs.xyz también corre en este VPS

---

## VPS-3 · VPS-OIC

> ✅ SSH verificado 2026-05-13 — specs reales obtenidos

| Campo | Valor |
|---|---|
| Hostname real | `srv1254764` |
| Proveedor | Hostinger |
| Región | (por confirmar) |
| OS | Ubuntu 22.04.5 LTS |
| Specs reales | 2 vCPU / 7937 MB RAM (~8 GB) / 97 GB disco |
| RAM en uso | 3945 / 7937 MB (49%) |
| Disco en uso | 53 GB / 97 GB (54%) |
| Load avg | 0.14 / 0.10 / 0.09 |
| Docker | v29.2.0 |
| IP pública | `31.220.58.97` |
| IP Tailscale | (pendiente — no instalado aún) |
| SSH user NOC | `root` |
| Rol en NOC | Monitoreado por SSH desde VPS-MyRock |

### Docker Compose projects

| Proyecto | Containers | Notas |
|---|---|---|
| `sistema-declaraciones` | frontend (8080), backend (3000), mongodb, reportes (3001), elasticsearch | SiDeclara — Declaraciones patrimoniales |
| `sier` | sier_app (→8090), sier_db (MariaDB 11) | Sistema de Entrega-Recepción |
| `denuncia-oic` | postgres, redis, minio (9000-9001), oic_sync | Sistema de Denuncias OIC |
| `oic` | oic_dashboard (Streamlit, 8501), oic_sqlserver (SQL Server 2022) | Dashboard analítico + BD legado |

### PM2 processes

| Nombre | Puerto | Uptime | Reintentos |
|---|---|---|---|
| oic-portal | 3005 | 15 días | 2 |
| oic-api | 3001 | 15 días | 3 |
| oic-panel | 3004 | 15 días | 2 |

### Dominios verificados (nginx)

| Dominio | Sistema | URL check | SSL | Criticidad |
|---|---|---|---|---|
| `declaraciones.cedhsinaloa.org.mx` | SiDeclara (frontend:8080 + backend:3000) | `https://declaraciones.cedhsinaloa.org.mx/` | ⚠️ solo HTTP — sin cert | high |
| `oic.cedhsinaloa.org.mx` | Portal OIC (PM2 oic-portal:3005) | `https://oic.cedhsinaloa.org.mx/` | ✅ Let's Encrypt | high |
| `sier.cedhsinaloa.org.mx` | SIER (sier_app:8090) | `https://sier.cedhsinaloa.org.mx/` | ✅ Let's Encrypt | high |

### Certificados SSL

| Cert | Dominios | Estado |
|---|---|---|
| oic.cedhsinaloa.org.mx | oic.cedhsinaloa.org.mx | verificar días |
| sier.cedhsinaloa.org.mx | sier.cedhsinaloa.org.mx | verificar días |
| declaraciones.cedhsinaloa.org.mx | **sin SSL** ⚠️ — corre HTTP | pendiente |

### Bloqueadores antes de monitoreo

- [x] Confirmar hostname, IP → srv1254764 / 31.220.58.97
- [x] Asegurar SSH desde VPS-MyRock funciona ✅
- [x] Confirmar dominios → declaraciones., oic., sier.cedhsinaloa.org.mx ✅
- [x] Confirmar motores DB → MariaDB 11, MongoDB, PostgreSQL, SQL Server 2022
- [ ] ⚠️ declaraciones.cedhsinaloa.org.mx corre sin SSL — reportar a Jorge

---

## VPS-4 · VPS-Mail (cedh-mail)

> ✅ SSH verificado 2026-05-13 — Tailscale instalado

| Campo | Valor |
|---|---|
| Hostname real | `mail-server-cedh` |
| Proveedor | Local (red CEDH Sinaloa) |
| Región | Culiacán, Sinaloa |
| OS | Ubuntu 24.04.4 LTS |
| Specs reales | 12 vCPU / 31784 MB RAM (~32 GB) / 915 GB disco |
| RAM en uso | 3498 / 31784 MB (11%) |
| Disco en uso | 93 GB / 915 GB (11%) |
| Load avg | 1.24 / 0.52 / 0.24 |
| Docker | v29.4.3 |
| Dominio principal | `mail.cedhsinaloa.org.mx` |
| IP local | `192.168.128.215` |
| IP Tailscale | `100.118.231.85` ✅ |
| SSH user NOC | `jyanagui` |
| Rol en NOC | Monitoreado vía Tailscale — **frágil, no tocar mucho** |

### Stack Mailcow (18 containers — proyecto `mailcowdockerized`)

| Container | Función | Puertos externos |
|---|---|---|
| nginx-mailcow | Reverse proxy + SSL termination | 80, 443 |
| postfix-mailcow | SMTP | 25, 465, 587 |
| dovecot-mailcow | IMAP/POP3 | 993, 995, 143, 110 |
| sogo-mailcow | Webmail SOGo | interno |
| rspamd-mailcow | Anti-spam | interno |
| clamd-mailcow | Antivirus ClamAV | interno (healthy) |
| mysql-mailcow | MariaDB 10.11 | 127.0.0.1:13306 |
| redis-mailcow | Redis 7.4.6 | 127.0.0.1:7654 |
| acme-mailcow | Gestor SSL automático | interno |
| watchdog-mailcow | Monitor interno | interno |
| unbound-mailcow | DNS resolver | interno (healthy) |

### SSL cert actual

| Dominio | CN | SANs cubiertos | Expira | Días |
|---|---|---|---|---|
| mail.cedhsinaloa.org.mx | whm.cedhsinaloa.org.mx | cedhsinaloa.org.mx, mail., webmail., cpanel., whm., www. | 2026-06-29 | ~47d ⚠️ warn pronto |

> Nota: el cert es de cPanel/WHM (no Let's Encrypt). `correo.cedhsinaloa.org.mx` (hostname interno) **no está en los SANs** — solo `mail.` es el acceso público.

### Mailcow config relevante

| Variable | Valor |
|---|---|
| MAILCOW_HOSTNAME | `correo.cedhsinaloa.org.mx` |
| TZ | `America/Mazatlan` |
| Acceso público | `mail.cedhsinaloa.org.mx` |

### Bloqueadores antes de monitoreo

- [x] Confirmar hostname → correo.cedhsinaloa.org.mx / acceso público: mail.cedhsinaloa.org.mx ✅
- [x] Tailscale instalado → 100.118.231.85 ✅
- [x] SSH desde VPS-MyRock funciona ✅
- [x] SSL cert verificado — expira 2026-06-29 (~47d)
- [ ] Confirmar DNS records (MX, SPF, DMARC) — Jorge lo tiene pendiente
- [ ] PTR de IP pública apunta a `mail.cedhsinaloa.org.mx`

---

## Servicios HTTP monitoreados (tabla maestra)

> Niveles de criticidad:
> - `high`: caída impacta operación CEDH directamente
> - `medium`: caída es molesta pero no operacional
> - `low`: experimental o personal

| Servicio | URL para check | Servidor | Criticidad | Estado |
|---|---|---|---|---|
| cedhsinaloa.org.mx | `https://cedhsinaloa.org.mx/` | vps-suig ✅ | high | verificado |
| SUIG | `https://suig.cedhsinaloa.org.mx/` | vps-suig ✅ | high | verificado |
| Buzón Electrónico | `https://buzon.cedhsinaloa.org.mx/` | vps-suig ✅ | high | verificado |
| SIER | `https://sier.cedhsinaloa.org.mx/` | vps-oic ✅ | high | verificado |
| Declaraciones | `http://declaraciones.cedhsinaloa.org.mx/` | vps-oic ✅ | high | ⚠️ HTTP only |
| Portal OIC | `https://oic.cedhsinaloa.org.mx/` | vps-oic ✅ | high | verificado |
| Mailcow SOGo | `https://mail.cedhsinaloa.org.mx/SOGo/` | vps-mail ✅ | high | verificado |
| Mailcow admin | `https://mail.cedhsinaloa.org.mx/` | vps-mail ✅ | medium | verificado |
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
- [ ] Confirmar dominios OIC (declaraciones, denuncias, ser-cedh)
- [x] Crear cuenta Tailscale e instalar en VPS-MyRock + Tab A8 ✅
- [x] Tailscale instalado en VPS-Mail (`100.118.231.85`) ✅
- [x] Crear llave SSH dedicada `noc_collector_ed25519` en VPS-MyRock ✅
- [x] Instalar llave pública en los otros 3 VPS ✅
- [x] Probar SSH desde VPS-MyRock con la llave dedicada ✅ (3/3 OK)
- [ ] Limpiar/identificar los 5 procesos PM2 huérfanos en VPS-MyRock
- [ ] Decidir si Evolution API v1 ya se puede apagar (queda v2)
- [ ] Actualizar SERVERS_CONFIG en .env del VPS con IPs y users reales
