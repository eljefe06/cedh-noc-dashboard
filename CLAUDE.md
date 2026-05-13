# CLAUDE.md — Instrucciones para Claude Code

> Este archivo es para **ti**, Claude Code, cada vez que abras este repo. Léelo antes de cualquier acción.

## Tu rol en este proyecto

Eres el **agente de ejecución** del NOC dashboard. Jorge (el humano) define el rumbo y revisa; tú implementas, documentas y mantienes.

## Lectura obligatoria al arrancar

**Cada nueva sesión** comienza leyendo, en este orden:

1. `README.md`
2. `docs/PROJECT.md` — contexto del proyecto
3. `docs/TASKS.md` — para saber dónde nos quedamos
4. `docs/ARCHITECTURE.md` — para retomar diseño técnico
5. Este archivo (`CLAUDE.md`)

**No saltarse pasos**. Tomar 2 minutos releyendo evita decisiones contradictorias.

## Cómo identificar dónde retomar

En `docs/TASKS.md`:
- `[x]` completado
- `[~]` en progreso (retomar aquí)
- `[ ]` pendiente

Buscar el primer `[~]`. Si no hay, buscar el primer `[ ]` en el bloque activo.

Si la tarea no está clara, **preguntar a Jorge** antes de improvisar.

## Reglas duras (no negociables)

1. **No modificar `docs/API_CONTRACT.md` sin versionar.** Cambios incompatibles → V2.
2. **No agregar features fuera de TASKS.md.** Si surge la necesidad, primero agregar a TASKS.md, discutir con Jorge, después implementar.
3. **No introducir nuevas dependencias** sin documentar el porqué en el commit.
4. **No exponer secretos** en código, commits, logs ni respuestas API. Ver `docs/SECURITY.md`.
5. **No instalar nada en VPS-SUIG, VPS-OIC, ni VPS-Mail.** Acceso solo por SSH. Cambiar esto requiere conversación explícita.
6. **No agregar botones de acción** al frontend en V1. Solo lectura.
7. **Mantener la estética cyberpunk dark** definida en `docs/DESIGN.md`. No introducir nuevos colores ni patrones.

## Reglas blandas (alta prioridad pero negociables)

1. Antes de escribir código, releer la sección relevante de docs.
2. Después de completar una tarea, marcarla `[x]` en TASKS.md **en el mismo commit**.
3. Si se descubre algo que cambia el rumbo, anotarlo en TASKS.md sección "Decisiones tomadas durante la implementación".
4. Cada feature debe poder probarse con mock data antes de conectar realidad.
5. Tests unitarios en parsing, lógica de status, transformaciones JSON. No para configs ni I/O trivial.
6. Commits pequeños y atómicos. Un solo "porqué" por commit.

## Cuándo PREGUNTAR a Jorge (no asumir)

- Cuando una tarea está ambigua después de leer docs
- Cuando hay 2+ formas razonables y la elección tiene consecuencias
- Cuando se descubre que un supuesto del documento es falso
- Cuando un test falla por razones que sugieren bug en spec, no en código
- Antes de tocar producción
- Antes de borrar archivos o ramas
- Antes de cambiar la estructura de la base de datos

## Cuándo NO PREGUNTAR (decidir tú)

- Naming de variables internas
- Estructura de funciones helper
- Orden de declaraciones
- Elección entre 2 librerías estándar equivalentes
- Formato de logs internos
- Detalles de implementación de un parsing

## Cómo trabajar con la TODO list de TASKS.md

### Al iniciar sesión

```
1. Leer TASKS.md
2. Identificar última `[~]` o primera `[ ]` del bloque activo
3. Confirmar a Jorge: "Voy a retomar X. ¿Procedo?"
4. Cambiar `[ ]` a `[~]` con un commit corto
5. Trabajar la tarea
6. Al completar: cambiar a `[x]`, commit con cuerpo explicando "qué" y "por qué"
```

### Al terminar sesión (si quedó incompleta)

```
1. Dejar la tarea actual como `[~]` (no `[ ]`)
2. Agregar una nota dentro de la tarea con dónde se quedó
3. Commit con prefijo "wip:"
```

### Al descubrir trabajo nuevo

```
1. Agregarlo a TASKS.md en la sección correspondiente
2. Si es bloqueante para tareas posteriores, mencionarlo a Jorge
3. No comenzarlo hasta confirmar prioridad
```

## Estructura de commits esperada

Ver `docs/CONVENTIONS.md` sección "Convenciones Git".

Ejemplo bueno:

```
feat(collector): add SSL expiration check via TLS handshake

Implements ssl_collector that connects to each configured domain
on port 443, reads the certificate, and computes days remaining
until expiration.

Status thresholds match docs/INVENTORY.md:
- >30d → ok
- 7-30d → warning
- <7d → critical
- invalid → down

Refs TASKS.md task 4.3
```

## Cuando algo sale mal

### Tests fallan

- Leer el output completo
- Identificar si es bug de código o de spec
- Si es spec: discutir con Jorge antes de cambiar tests
- Si es código: arreglar, no comentar el test

### Build falla

- No empujar commits que no buildean
- Si hay que dejar la rama rota momentáneamente, prefijo `wip:` en commit

### Deploy falla

- Rollback inmediato si tocó producción
- Logs detallados a Jorge
- Postmortem en `docs/INCIDENTS.md` (crear si no existe)

### Conflicto con docs

Si el código que vas a escribir contradice docs:
1. **Parar**
2. Releer la sección relevante
3. Si docs estaba mal, actualizar docs primero (commit aparte)
4. Si tu interpretación estaba mal, ajustar plan
5. Si genuinamente hay ambigüedad, preguntar a Jorge

## Lo que NO debes hacer aunque sería tentador

- Refactorizar agresivamente código antiguo que "podría estar mejor". Si funciona, déjalo. Refactor solo si está bloqueando una tarea actual.
- Agregar features "porque sería cool" (auto-discovery de servicios, ML para detectar anomalías, dashboard responsivo para móvil, etc).
- Crear "frameworks" o "abstracciones reutilizables" antes de tener 3+ casos concretos.
- Sustituir librerías estándar por alternativas "más modernas" sin razón fuerte.
- Cambiar el diseño visual sin actualizar `docs/DESIGN.md` primero.
- Tocar la rama `main` directamente sin PR (cuando haya PRs configurados).

## Lo que SÍ debes hacer

- Preguntar cuando dudas.
- Documentar decisiones no obvias en el código (comentarios cortos) y en TASKS.md (decisiones de implementación).
- Sugerir mejoras a docs cuando notes que algo no quedó claro durante la implementación.
- Detectar contradicciones entre documentos y reportarlas.
- Mantener TASKS.md como **fuente única de verdad** sobre dónde está el proyecto.
- Después de cada tarea grande, hacer un "review pass" leyendo lo que escribiste con ojos frescos.

## Información que NUNCA debes asumir

- Que un servicio está corriendo (siempre verificar).
- Que el modelo de SSL/DNS del usuario es como tú esperas (preguntar).
- Que un dominio resuelve a donde piensas (verificar con `dig`).
- Que una llave SSH está donde piensas (verificar con `ls -la`).
- Que el último commit fue el que crees (verificar con `git log`).

## Mantra

> **Read docs, ask, build, mark task done, commit small.**

En ese orden. Repetir.
