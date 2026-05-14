# DESIGN.md — Sistema de diseño operativo cyberpunk

## Filosofía visual (cerrada)

> "Tablero de guerra cyberpunk. La estética sirve al problema, no al revés."

El dashboard responde **4 preguntas operativas** en orden de prioridad:

1. **¿Está bien?** → Header con contadores grandes (1 crítico, 1 advertencia, 11 ok)
2. **¿Qué pasó?** → Incidentes activos en bloque prominente con título humano
3. **¿A quién afecta?** → Badge de impacto explícito en cada incidente
4. **¿Qué hago?** → Línea de diagnóstico con `→` y acción sugerida

Si una zona visual del dashboard no responde una de estas preguntas, **no debe estar ahí**.

## Anti-patrones (errores que NO se repiten)

> Aprendidos del primer prototipo. Documentados para no caer en ellos otra vez.

### ❌ Uniformidad democrática
Cuando todas las cards se ven igual de importantes, lo crítico se pierde. Las cards deben tener **disparidad visual** según urgencia.

### ❌ Estética sobre función
Una grid de 12 cajitas neón se ve cool pero no comunica jerarquía. La estética cyberpunk se subordina a la utilidad operativa.

### ❌ Métricas puras sin diagnóstico
"CPU 12%" no le dice a nadie qué hacer. "Cloudflare 520 + VPS vivo = problema entre Cloudflare y origen" sí.

### ❌ Mezclar capas (infra y servicios)
Un VPS sano no significa que el servicio público funciona. Hay que separar visualmente "salud del host" de "salud del servicio".

### ❌ Tiempos pequeños
La duración de un incidente es **la métrica más importante** durante una crisis. Un 520 de 30 segundos no es nada, de 14 minutos es batalla. Los tiempos de incidente activo van **grandes**.

## Reglas inviolables

1. **Jerarquía visual = jerarquía de urgencia**. Lo crítico ocupa más superficie visual.
2. **Disparidad por sobre uniformidad**. Cards de igual tamaño solo cuando están en igual condición.
3. **Diagnóstico humano**, no metric raw.
4. **Densidad alta pero respirada** — caben muchos datos sin ahogar.
5. **Glow real** con `box-shadow` y `text-shadow`, no gradientes pastel.
6. **Tipografía monoespaciada** en todo el dashboard.
7. **Sin emoji** en la UI (solo en loading messages).
8. **Sin imágenes raster** — todo SVG o CSS.
9. **Sin animaciones que distraigan** — solo `pulse-crit` (contador crítico) y `blink` (servicio caído).
10. **Sin scroll horizontal** — todo cabe en 1280x800 efectivo.
11. **Sin botones de acción en V1** — solo lectura.
12. **Estados visuales claros** — lima=ok, naranja=warning, magenta=crítico/caído, cyan=info.

## Paleta cerrada

```css
/* Fondo */
--bg-base: #0a0612;
--bg-elevated: #110820;
--bg-inset: #050208;
--bg-header: #14081c;
--bg-incident-crit: #1a0810;
--bg-incident-warn: #1a1208;
--bg-vps-sano: #0d0518;
--bg-status-bar: linear-gradient(90deg, #2a0a14 0%, #14081c 100%);

/* Acentos neón */
--neon-lime: #c6ff00;
--neon-cyan: #00e5ff;
--neon-magenta: #ff2d95;
--neon-orange: #ff9500;

/* Texto */
--text-primary: #e8e0ee;
--text-secondary: #a89cb4;
--text-tertiary: #7a6890;
--text-muted: #5a4870;

/* Bordes */
--border-default: #2a1838;
--border-inset: #1a0d28;

/* Glow */
--glow-lime: 0 0 6px rgba(198, 255, 0, 0.6);
--glow-cyan: 0 0 6px rgba(0, 229, 255, 0.6);
--glow-magenta-strong: 0 0 12px #ff2d95;
--glow-orange: 0 0 6px rgba(255, 149, 0, 0.5);
```

## Tipografía

**JetBrains Mono** self-hosted en `frontend/assets/fonts/`. Fallback a Fira Code, SF Mono, Monaco, monospace.

### Tamaños

```css
--text-xs: 9px;     /* Logs, section dividers, footer */
--text-sm: 10px;    /* Service names, metadata, line items */
--text-base: 11px;  /* Header items, descripciones de incidente */
--text-md: 13px;    /* Títulos de incidente */
--text-lg: 18px;    /* Duración de incidente */
--text-xl: 22px;    /* Contadores del header (1 CRIT, 1 WARN, 11 OK) */
```

### Pesos

Solo `400` (regular) y `500` (medium). **Nunca bold**.

### Mayúsculas vs minúsculas

- **MAYÚSCULAS** con letter-spacing 1-2px: labels, badges, nombres de servidor, footer
- **minúsculas**: nombres de servicio, comandos, hashes, dominios
- **Título de incidente**: oración natural en español
- **Descripción de incidente**: prosa natural

## Layout 1280x800 efectivo

```
┌──────────────────────────────────────────────────────────┐
│ STATUS BAR (52px)                                        │
│   ESTADO GLOBAL  [1 CRIT] [1 WARN] [11 OK]  uptime time  │
├──────────────────────────────────────────────────────────┤
│ INCIDENTES ACTIVOS (~180px, dinámico)                    │
│   [CRÍTICO] Título humano                       14m      │
│   Descripción contextual                                 │
│   → Diagnóstico probable y acción         [BADGE IMPACTO]│
├──────────────────────────────────────────────────────────┤
│ // servicios públicos (~62px)                            │
│   8 chips compactos en fila                              │
├──────────────────────────────────────────────────────────┤
│ // infraestructura (~58px)                               │
│   4 VPS cards horizontales compactas                     │
├──────────────────────────────────────────────────────────┤
│ PANELES OPERATIVOS (~150px)                              │
│   [últimos cambios] [certificados] [pendientes hoy]      │
├──────────────────────────────────────────────────────────┤
│ FOOTER (24px)                                            │
└──────────────────────────────────────────────────────────┘
```

### Filosofía del layout

- **Lo más urgente arriba** (status bar + incidentes activos)
- **Lo que respira abajo** (servicios sanos comprimidos)
- **Lo contextual al final** (cambios, certs, pendientes)
- **Si no hay incidentes activos**, el bloque colapsa y el resto sube

## Componentes (especificación)

### Status Bar

- Fondo: gradient `--bg-status-bar` (magenta tinted del lado izquierdo)
- Border bottom: 2px magenta
- Contadores con número `22px` y label `10px UPPERCASE`
- **El contador crítico parpadea** (`pulse-crit` 1s) si >0
- Si críticos=0: contador en color tertiary sin glow
- Meta a la derecha: uptime + hora en UPPERCASE letter-spacing 1px

### Incidente activo

- Border-left grueso (4px) en color de severidad
- Fondo: `--bg-incident-crit` o `--bg-incident-warn`
- Tag superior: pill UPPERCASE con fondo del color de severidad
- Título: 13px medium, español natural
- Descripción: 11px secondary
- Diagnóstico: 10px cyan, prefijo `→ ` lima
- Lado derecho: duración prominente (18px medium) + badge de impacto

**Tipos de impacto** (badges):
- `Afecta usuarios públicos` → magenta
- `Afecta operación interna` → magenta
- `Sin impacto operativo` → naranja
- `Solo monitoreo` → naranja

### Service chip

- 8 chips en grid `repeat(8, 1fr)` gap 4px
- Border-top 3px del color de estado (lima/naranja/magenta)
- Nombre en lowercase, truncado con ellipsis
- Meta: latencia · status, o error abreviado si caído
- **Sin pill, sin badge** — el border-top basta

### VPS card

- 4 cards en grid `repeat(4, 1fr)` gap 6px
- Fondo: `--bg-vps-sano` (bajo perfil)
- Indicador 8px con glow del color
- Nombre UPPERCASE letter-spacing 0.5px medium
- Stats en línea: `cpu N  ram N  dsk N`
- Si métrica está en warn/crit: color del valor cambia
- **Sin barras de progreso** — son ruido para VPS sano

### Section divider

- `// servicios públicos ─────────────────────`
- Texto 9px UPPERCASE letter-spacing 2px en `--text-tertiary`
- Línea horizontal degradada después

### Panel operativo (3 paneles)

- 3 paneles en grid `repeat(3, 1fr)` gap 6px
- Fondo `--bg-inset`, border 1px `--border-inset`
- Título 9px lima UPPERCASE letter-spacing 2px con prefijo `// `
- Líneas 10px con timestamp en muted, contenido en primary
- Tags: `deploy` cyan, `backup` lima, `incident` magenta

### Footer

- Background `--bg-header`
- Border-top 1px `--border-default`
- 9px UPPERCASE letter-spacing 1px en `--text-tertiary`
- `ONLINE` en lima con glow

## Animaciones permitidas

```css
@keyframes pulse-crit {
  0%, 100% { opacity: 1; }
  50%      { opacity: 0.5; }
}
/* SOLO en contador crítico del header cuando >0 */

@keyframes blink-service {
  0%, 100% { opacity: 1; }
  50%      { opacity: 0.6; }
}
/* SOLO en chips de servicios caídos */
```

**Prohibido**: slide, bounce, fade-in al cargar, parallax, ripples, hover scale, transiciones en hover.

## Estados especiales

### Sin incidentes activos

Bloque de incidentes muestra una sola línea:

```
┌────────────────────────────────────────────┐
│ ✓ Sin incidentes activos                   │
│   Todos los servicios responden normal     │
└────────────────────────────────────────────┘
```

- Fondo `--bg-elevated`, border 1px lima
- Texto en lima con glow sutil
- Mucho más compacto que un incidente real

### API no responde

Overlay top-center:

```
┌────────────────────────────────────────────┐
│ ☓ API SIN RESPUESTA                        │
│ Último estado: hace 47s · Reintentando...  │
└────────────────────────────────────────────┘
```

- Fondo magenta tinted, border magenta blink
- No reemplaza la vista (último estado conocido visible grised)
- Cuando API responde: desvanece 200ms (única transición permitida)

### Tablet en portrait

Pantalla completa centrada con `↻ ROTA LA TABLET A HORIZONTAL`.

## HUD brackets

Solo en:
- **Incidentes**: border-left grueso 4px (más fuerte que bracket)
- **Service chip**: border-top 3px
- **Paneles operativos**: bracket magenta opcional esquina superior izquierda

**No** en VPS cards ni status bar (saturaría).

## Scanlines

Sutiles en fondo del screen, no en cards:

```css
background:
  radial-gradient(ellipse at top, rgba(255, 45, 149, 0.06) 0%, transparent 50%),
  radial-gradient(ellipse at bottom right, rgba(0, 229, 255, 0.05) 0%, transparent 50%),
  repeating-linear-gradient(0deg, transparent 0, transparent 2px, rgba(255, 255, 255, 0.012) 2px, rgba(255, 255, 255, 0.012) 3px),
  var(--bg-base);
```

## Iconos

**No librerías**. Caracteres Unicode permitidos:
- `→` (en diagnósticos)
- `●` (estado de VPS)
- `✓` (estado vacío sano)
- `☓` (estado de error)
- `↻` (rotación)
- `//` (prefijo de secciones)
- `─` (separadores)

## Decisiones revertidas

Quitado del diseño anterior:

| Quitado | Razón |
|---|---|
| Grid 4×2 de service cards con sparkline | Uniformidad democrática |
| Sparklines en cada servicio | Bonitos pero no informativos a esa escala |
| KPIs operativos CEDH (quejas, firmas) | No es panel CEDH, es NOC técnico |
| Pills de status code en cada servicio | Demasiado peso visual para servicios OK |
| Barras de progreso en VPS sanos | Ruido visual |
| Panel `stdout.live` extensivo | Movido a V2 |

## Capas visuales (jerarquía)

1. **Capa alarma** (status bar + incidentes activos): más prominente, más altura, color saturado
2. **Capa estado actual** (servicios + infra): compacta, fondo intermedio
3. **Capa contexto** (paneles operativos): fondo oscuro, tipografía menor, info histórica

Esta jerarquía hace que la mirada llegue primero a lo urgente.

## Responsive

V1 **solo landscape 1280x800**. Tablet kiosko. V2 puede agregar mobile si Jorge lo necesita para ver desde el celular fuera de oficina.
