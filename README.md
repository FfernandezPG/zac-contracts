# zac-contracts

Los contratos versionados de Zac: la **única dependencia común que DIP permite**.
Ningún módulo define su propio formato de estos artefactos; todos cuelgan de acá.

## Qué es canónico

El **artefacto canónico es el JSON versionado**, en `schemas/`. Es
language-agnostic: viaja con su versión en el `$id` y no depende de ningún
lenguaje. El paquete Python (`zac_contracts/`) es solo un **binding**: empaqueta
y entrega esos JSON a los consumidores Python. Cuando lleguen módulos Node
(Etapa 5), se agrega un binding Node que empaqueta **los mismos** JSON — aditivo,
no re-versionado.

## Layout

```
schemas/
  v1/                         # contratos estables, congelados
    manifest.schema.json
    ledger-event.schema.json
  draft/                      # inestable, NO viaja en el paquete estable
    handoff-artifact.schema.json
zac_contracts/                # binding Python
  __init__.py
  loader.py
pyproject.toml                # empaqueta SOLO schemas/v1 en el wheel
```

## Versionado

- La versión vive en el `$id` de cada esquema (`.../v1/...`), donde JSON Schema
  la quiere, y viaja con el archivo.
- `manifest` y `ledger-event` están **congelados a v1**. Cambiarlos es un bump
  con reglas SemVer.
- `handoff-artifact` está en **`draft/`**: tiene cero consumidores reales hasta
  Etapa 5 (dsc-sdd → sdd-model). Se congela a v1 cuando un caso real lo ejercite.
  **No viaja en el distribuible estable** — nadie debe depender de él por accidente.
- Los tags de git son scopeados por componente (ej: `contracts-v1.0.0`).

## Binding Python

```python
from zac_contracts import load_schema, schema_path, event_types

load_schema("manifest")       # dict del JSON Schema del manifiesto v1
load_schema("ledger-event")   # dict del JSON Schema del evento de ledger v1
event_types()                 # ('invocation', 'gate_signature', 'ingestion', 'error')
```

`event_types()` se **deriva** del `ledger-event.schema.json` empaquetado: es la
fuente de verdad única del enum, para que el SDK deje de hardcodearlo.

## Reglas de diseño registradas

- `ledger-event` queda **abierto** (sin `additionalProperties: false`) a
  propósito: la capa de escritura del SDK agrega `event_id` (clave de fila, no
  contenido del evento) después de validar. Documentado en el `$comment` del
  propio esquema. No cerrar sin resolver eso primero.
- `audit.events` del manifiesto es la **cota superior** de lo que un módulo tiene
  permitido escribir al ledger (declaración de capacidad, no de comportamiento
  actual). Su enum espeja el de `event_type`; el auditor determinista asserta que
  ambos coincidan.
