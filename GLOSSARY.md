# GLOSSARY.md — Glosario del dominio

## Términos del CEDH

**CEDH Sinaloa**: Comisión Estatal de los Derechos Humanos de Sinaloa. Organismo público autónomo.

**UDIyS**: Unidad de Diseño Institucional y Sistemas. Área que dirige Jorge dentro del CEDH.

**OIC**: Órgano Interno de Control. Área de contraloría/auditoría con sistemas propios (Declaraciones, Denuncias).

**Secretaría Ejecutiva**: área dirigida por Marcela Adriana Flores.

**Secretaría Técnica**: área dirigida por José Pablo Balderas.

**Jefe de Sistemas**: Sergio Hernández Chávez, colega de Jorge.

## Sistemas institucionales

**SUIG**: Sistema Único de Información para la Gestión (quejas). Sistema principal del CEDH para captura, seguimiento y gestión de expedientes de quejas por presuntas violaciones a derechos humanos. Stack: Node.js/PHP en Docker (por confirmar).

**SER-CEDH / CEDH-SIER**: Sistema de Entrega-Recepción de la CEDH. Para handover entre administraciones. Stack: Laravel (por confirmar). Vive en VPS-OIC.

**Declaraciones**: Sistema de declaraciones patrimoniales. Integra con la PDN (Plataforma Digital Nacional). Vive en VPS-OIC.

**Denuncias**: Sistema de denuncias del OIC. Vive en VPS-OIC.

**Mesa de Control**: Módulo de SUIG para distribución de quejas entre visitadores.

**Buzón Electrónico**: Sistema de notificaciones electrónicas oficiales. Dominio: `buzon.cedhsinaloa.org.mx`.

**Mailcow**: Stack de correo electrónico institucional. Vive en VPS-Mail. Dominio: `mail.cedhsinaloa.org.mx`.

**SGDA**: Sistema de Gestión Documental y Archivo. Laravel 11. (No confirmado si en V1 se monitorea.)

**MIR**: Matriz de Indicadores para Resultados. WordPress plugin para tracking.

**cedhs.xyz**: Acortador URL del CEDH. Vive en VPS-SUIG.

**PDN**: Plataforma Digital Nacional. Sistema federal de transparencia con el que Declaraciones se integra vía OAuth2.

## Términos personales / freelance

**MyRock**: Agencia digital de Jorge. Stack en VPS-MyRock.

**PagoKids**: Plataforma de pagos NFC para cafeterías escolares co-fundada por Jorge.

**ChatRock**: SaaS de Jorge (en desarrollo).

**Naibi Concept Store**: Boutique de ropa femenina co-administrada con su pareja Naibi.

**BetTracker**: Sistema cuantitativo de análisis de player props MLB que Jorge desarrolla.

## Términos de infraestructura

**OpenClaw**: Alias humano del VPS-MyRock (srv1386238). Se usaba como hostname conceptual antes de saber que era el mismo servidor.

**VPS**: Virtual Private Server.

**Hetzner**: Proveedor cloud alemán donde viven VPS-MyRock y posiblemente VPS-SUIG y VPS-OIC.

**Contabo**: Proveedor cloud alemán donde vive VPS-Mail.

**Tailscale**: Red privada virtual (mesh VPN) que se usa para que el dashboard solo sea accesible desde dispositivos autorizados.

**ControlMaster**: Feature de SSH que mantiene conexiones persistentes para reutilización rápida.

**Node Exporter**: Agente de Prometheus que expone métricas de sistema. **No se usa en V1** pero podría en V2.

**FastAPI**: Framework Python async para APIs.

## Términos del NOC dashboard

**NOC**: Network Operations Center. Centro de operaciones de red. Pantalla de monitoreo central.

**Polling**: Estrategia de revisar estado preguntando cada X segundos (vs push).

**ControlPath / ControlMaster / ControlPersist**: Trío de opciones SSH para conexiones persistentes.

**Sparkline**: Mini-gráfica inline de tendencia (SVG en este proyecto).

**HUD**: Heads-Up Display. Las esquinas decorativas con brackets vienen de esta estética.

**Glow**: Efecto luminoso con `box-shadow` y `text-shadow` que da apariencia neón.

**Scanlines**: Líneas horizontales sutiles que evocan pantallas CRT antiguas.

**Status pill**: Indicador colorido pequeño con código HTTP o latencia.

**Health check**: Endpoint que devuelve estado de un servicio (típicamente `/health`).

**Discovery**: Proceso de descubrir qué corre en un servidor sin conocimiento previo.

**Collector**: Componente del NOC que recolecta un tipo de dato (HTTP, SSH, DNS, SSL).

**Cache TTL**: Tiempo de vida del cache antes de refrescar.

**Stale**: Datos viejos servidos cuando la fuente no responde.

**Drill-down**: Vista detallada de un elemento al hacer click/tap.

## Niveles de estado

**`ok`**: Todo bien, en parámetros normales.

**`warning`**: Degradado pero funcional. Atención no inmediata.

**`critical`**: Cerca del fallo o método crítica fuera de rango. Atención inmediata.

**`down`**: No responde. Solo aplica a servicios. Para métricas de recursos se usa `critical`.

**`unknown`**: No se pudo determinar. Agente no responde o error de check.

## Criticidad de servicios

**`high`**: Caída afecta operación CEDH (correo, SUIG, sitio público, sistemas OIC).

**`medium`**: Caída es molesta pero no operacional crítica (acortador, dashboards internos).

**`low`**: Experimental o producto personal sin impacto operativo.

## Tipos de check

**HTTP**: GET a URL, valida status code y mide latencia.

**TCP**: Solo verifica que el puerto acepta conexión.

**SMTP**: TCP + STARTTLS handshake exitoso.

**IMAP**: TCP + TLS handshake exitoso.

**TLS/SSL**: Conecta y lee certificado, calcula días restantes.

**DNS**: Consulta DNS contra resolver externo (1.1.1.1, 8.8.8.8).

**PTR**: DNS inverso desde IP a hostname.

**Process**: Verifica que un proceso/container está corriendo.

**Queue**: Verifica longitud de cola (Postfix queue, Redis queue, etc.).

## Términos personales de Jorge (contexto del operador)

**Darién**: Hijo de Jorge.

**Naibi**: Pareja de Jorge.

**Karol**: Colega y amiga de Jorge en CEDH. Hay una memoria explícita: no mencionarla en canciones o parodias relacionadas con CEDH.

**Yanagui**: Apellido japonés de Jorge, herencia de su bisabuelo emigrado del Pacífico.

**Rubiera**: Línea genealógica que Jorge investiga para la nacionalidad española por Ley de Memoria Democrática.

**Cowork**: Producto de Anthropic. También nombre del Obsidian vault personal de Jorge ("Claude Cowork").
