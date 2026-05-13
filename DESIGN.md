# DESIGN.md — Sistema de diseño cyberpunk dark

## Filosofía visual

> "Akira en pleno turno nocturno. Una cabina de mando, no un dashboard institucional."

El dashboard debe sentirse **personal y técnico**, no corporativo. Cuando Jorge voltea desde el monitor principal hacia la Tab A8, su cerebro debe entrar en modo systems-engineer instantáneamente, no en modo "ver gráficas bonitas".

## Reglas inviolables

1. **Densidad alta pero respirada** — caben muchos datos sin que se sienta apretado
2. **Glow real con `box-shadow` y `text-shadow`**, no gradientes pastel
3. **Tipografía monoespaciada** en todo el dashboard (números, hashes, tiempos, dominios — todo se alinea)
4. **Sin emoji** en la UI (solo en loading messages)
5. **Sin imágenes raster** — todo SVG o CSS
6. **Sin animaciones que distraigan** — solo pulse en heartbeat global y blink en servicios caídos
7. **Sin scroll horizontal** — todo cabe en 1280px landscape
8. **Sin botones de acción en V1** — solo lectura
9. **Estados visuales claros** — verde lima = ok, naranja = warning, magenta = caído, cyan = info neutra

## Paleta cerrada

### Fondo

```css
--bg-base: #0a0612;          /* Púrpura casi negro */
--bg-elevated: #110820;      /* Cards y paneles */
--bg-inset: #050208;         /* Sparklines y zonas embebidas */
--bg-header: #14081c;        /* Header y footer */
```

### Acentos neón (los 4 colores semánticos)

```css
--neon-lime:    #c6ff00;     /* OK · todo bien · success */
--neon-cyan:    #00e5ff;     /* Info · sparklines · metadatos */
--neon-magenta: #ff2d95;     /* DOWN · caído · alerta crítica · branding */
--neon-blue:    #00aaff;     /* WARNING · degradado · atención */
```

> **Accesibilidad (deuteranopia)**: el operador (Jorge) es deutan. El orange original (#ff9500)
> era indistinguible del lime para él — ambos aparecen como amarillo-pardo. Se reemplazó por
> azul (#00aaff), claramente distinguible del amarillo para deutans. Los símbolos ▲ (warning)
> y ✕ (critical/down) se agregan a las pills para que el estado no dependa únicamente del color.

### Texto

```css
--text-primary: #e8e0ee;     /* Texto principal */
--text-secondary: #a89cb4;   /* Labels, meta info */
--text-tertiary: #7a6890;    /* Hints, footer */
--text-muted: #5a4870;       /* Timestamps en logs */
```

### Bordes

```css
--border-default: #2a1838;   /* Bordes de cards */
--border-accent: #ff2d95;    /* Acentos magenta en bordes top */
```

### Glow values (sombras de luz)

```css
--glow-lime:    0 0 6px rgba(198, 255, 0, 0.6);
--glow-cyan:    0 0 6px rgba(0, 229, 255, 0.6);
--glow-magenta: 0 0 8px rgba(255, 45, 149, 0.7);
--glow-blue:    0 0 6px rgba(0, 170, 255, 0.6);
```

## Tipografía

### Fuente

**Principal**: monoespaciada del sistema con stack de fallbacks.

```css
font-family: 
  'JetBrains Mono',
  'Fira Code',
  'SF Mono',
  Monaco,
  'Cascadia Code',
  'Roboto Mono',
  Consolas,
  'Courier New',
  monospace;
```

Si se quiere consistencia total, descargar **JetBrains Mono** localmente y servir desde el frontend (self-hosted, no Google Fonts).

### Tamaños

```css
--text-xs: 9px;     /* Logs, labels secundarios, status pills */
--text-sm: 10px;    /* Service names, metadata */
--text-base: 11px;  /* Header items, KPIs */
--text-md: 12px;    /* Server names */
--text-lg: 13px;    /* Métricas grandes */
--text-xl: 18px;    /* KPI values */
```

### Pesos

Solo dos:
- `400` (regular) para body y meta
- `500` (medium) para énfasis, nombres, valores destacados

**Nunca `bold` (700)** — rompe la estética monospace ligera.

### Mayúsculas vs minúsculas (regla)

- **MAYÚSCULAS con letter-spacing 1-2px**: labels, etiquetas, nombres de servidor, navegación
- **minúsculas**: nombres de servicio (`cedhsinaloa.org.mx`, `suig.cedh`), comandos, hashes
- **Title Case**: solo en headers de modales (V2)

## Layout

### Estructura horizontal (Tab A8 landscape, 1280x800 efectivo)

```
┌─────────────────────────────────────────────────────────┐
│ HEADER (32px alto)                                      │
├─────────────────────────────────────────────────────────┤
│ TOP ROW · 4 cards VPS (1/4 ancho c/u)        (~100px)   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ SERVICES GRID · 4×2 = 8 cards de servicio    (~280px)   │
│                                                         │
├─────────────────────────────────────────────────────────┤
│ BOTTOM ROW · logs / SSL / deploys (1/3 c/u)   (~140px)  │
├─────────────────────────────────────────────────────────┤
│ FOOTER (20px alto)                                      │
└─────────────────────────────────────────────────────────┘
```

### Gaps y padding

```css
--gap-xs: 3px;
--gap-sm: 4px;
--gap-md: 6px;
--gap-lg: 8px;
--gap-xl: 14px;

--pad-card: 8px 10px;
--pad-header: 8px 14px;
--pad-footer: 4px 14px;
```

### Border radius

**Mínimo o cero**. La estética cyberpunk no usa esquinas redondeadas. Cards rectangulares con esquinas decorativas tipo HUD.

```css
--radius-none: 0;            /* Por defecto */
--radius-pill: 0;            /* Status pills también rectangulares */
```

## Componentes

### Header

```
[●pulse] [UDIyS] NOC.MESH // CDX-SIN          UP 14D 06:42 · INC 1 · LOAD 0.42 · 10:42:18
```

- Pulse animado verde lima en heartbeat (2s loop)
- Tag `[UDIyS]` en fondo magenta con texto oscuro
- `// CDX-SIN` en cyan
- Métricas a la derecha en tabular-nums

### VPS Card

```
┌─────────────────────────────────┐
│ ▸ OPENCLAW    HZN·NBG1 // 2c/4g │
├─────────────────────────────────┤
│ CPU  RAM  DISK  NET             │
│ 12%  48%  34%   2.1M            │
│ ▓▓░░ ▓▓▓░ ▓░░░  ▓▓░░            │
└─────────────────────────────────┘
```

- Border izquierdo grueso (4px) en color de estado
- Esquina superior derecha: HUD bracket cyan
- Nombre con `▸ ` magenta antes
- Metrics en grid 1×4
- Barras con glow del color de estado

### Service Card

```
┌──────────────────────┐
│ ─────────────────    │ <- border top de 2px en color de estado
│ suig.cedh  [142ms]   │
│ p95          198ms   │
│ pm2     4 workers    │
│ ╱╲╱╲___╱╲╱╲___       │ <- sparkline cyan
└──────────────────────┘
```

- Border top de 2px en color de estado
- Nombre del servicio en lowercase
- Status pill a la derecha (verde lima si OK, naranja si warn, magenta si bad)
- 2 líneas de metadata
- Sparkline SVG en zona embebida oscura (h: 18px)

### Status pill

```css
.status-ok      { background: var(--neon-lime);    color: var(--bg-base); }
.status-warn    { background: var(--neon-blue);     color: var(--bg-base); }  /* azul, deutan-safe */
.status-bad     { background: var(--neon-magenta);  color: var(--bg-base); }
.status-unknown { background: var(--text-tertiary); color: var(--bg-base); }
```

Pills de warning muestran prefijo `▲`, pills critical/down muestran `✕` para no depender solo del color.

Todos con su correspondiente glow box-shadow. La pill `bad` parpadea cada 1.2s.

### Bottom panels (logs / SSL / deploys)

Fondo más oscuro que las cards (`--bg-inset`):

- Esquina superior izquierda: HUD bracket magenta
- Título en lima con `// prefix` (ej: `// stdout.live`, `// ssl.expiry`, `// git.deploys`)
- Contenido con tabular-nums

### Footer

```
// tailscale.mesh ONLINE · jorge@udiys              refresh 5s · v0.1 · build cdx-sin
```

- `ONLINE` en lima con glow
- Todo en uppercase, letter-spacing 1px
- Texto en tertiary muy bajo contraste

## Animaciones permitidas

```css
@keyframes cp-pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50%      { opacity: 0.5; transform: scale(1.3); }
}
/* Usar solo en heartbeat del header. */

@keyframes cp-blink {
  0%, 100% { opacity: 1; }
  50%      { opacity: 0.55; }
}
/* Usar solo en status pills de servicios DOWN. */
```

No agregar más animaciones sin actualizar este documento.

## Decoraciones HUD

Las cards llevan brackets en esquinas que dan sensación de HUD militar/cyberpunk:

```css
/* VPS card: bracket cyan en esquina superior derecha */
.vps-card::before {
  content: "";
  position: absolute;
  top: -1px; right: -1px;
  width: 14px; height: 14px;
  border-top: 1px solid var(--neon-cyan);
  border-right: 1px solid var(--neon-cyan);
  box-shadow: 0 0 6px rgba(0, 229, 255, 0.4);
}

/* Bottom panel: bracket magenta en esquina superior izquierda */
.panel::before {
  content: "";
  position: absolute;
  top: -1px; left: -1px;
  width: 12px; height: 12px;
  border-top: 2px solid var(--neon-magenta);
  border-left: 2px solid var(--neon-magenta);
  box-shadow: -2px -2px 6px rgba(255, 45, 149, 0.3);
}
```

## Scanlines

Sutiles, casi imperceptibles. Solo en el fondo del screen, no en cards:

```css
background:
  radial-gradient(ellipse at top, rgba(255, 45, 149, 0.06) 0%, transparent 50%),
  radial-gradient(ellipse at bottom right, rgba(0, 229, 255, 0.05) 0%, transparent 50%),
  repeating-linear-gradient(0deg, transparent 0, transparent 2px, rgba(255, 255, 255, 0.012) 2px, rgba(255, 255, 255, 0.012) 3px),
  var(--bg-base);
```

Los radiales de magenta y cyan suman ambiente sin distraer.

## Iconos

**No usar librerías de iconos** (no Lucide, no Heroicons, no FontAwesome). Si se necesita un icono:
- **Marcador**: caracter Unicode (`▸` `●` `▎` `◇`)
- **Visual**: SVG inline en el HTML
- **Estado**: pills de color, no iconos

## Estado vacío

Si un panel no tiene datos (ej: no hay incidentes):

```
// stdout.live
─ sin actividad reciente
```

Texto en `--text-muted` con guión inicial. Nunca dejar paneles vacíos en blanco.

## Estado de error

Si la API no responde:

```
┌─────────────────────────────────┐
│ ☓ API SIN RESPUESTA             │ <- magenta blink
│ Último estado: hace 47s         │
│ Reintentando...                 │
└─────────────────────────────────┘
```

Overlay sobre el dashboard, no reemplaza completamente la vista (deja ver el último estado conocido).

## Accesibilidad

Aunque la tablet es de uso personal:

- Contraste mínimo AA en texto importante
- `aria-label` en elementos interactivos
- `role="status"` en panel de estado global
- `aria-live="polite"` en logs en vivo (V2)

## Responsive

V1 **solo soporta landscape 1280x800**. Si la tablet rota a portrait, mostrar mensaje:

```
┌─────────────────────────────────┐
│ ↻                               │
│ ROTA LA TABLET A HORIZONTAL     │
│                                 │
│ Optimizado para landscape       │
└─────────────────────────────────┘
```

## Lo que NO está permitido

- ❌ Gradientes lineales en backgrounds (solo radiales sutiles en `--bg-base`)
- ❌ Border-radius mayor a 0
- ❌ Drop shadows pastel (usar siempre neón con glow)
- ❌ Bold weights (max 500)
- ❌ Animaciones de movimiento (slide, bounce, etc)
- ❌ Iconos de librerías
- ❌ Imágenes raster
- ❌ Modo claro (toggle de tema) en V1
- ❌ Skins alternativas o múltiples temas
