"""Binding Python fino de zac-contracts.

El artefacto canonico es el JSON versionado (language-agnostic, en schemas/).
Este paquete es solo el 'como lo consume Python': empaqueta los JSON v1 y los
entrega, mas una derivacion del enum de event_type para que el SDK deje de
hardcodearlo (D-D).

handoff-artifact NO esta aca: queda en schemas/draft/ y fuera del paquete
estable v1 (D-A). Este binding solo expone lo estable.
"""
from __future__ import annotations

import json
from functools import lru_cache
from importlib.resources import files
from pathlib import Path

# Version del contrato estable que empaqueta este binding.
CONTRACTS_VERSION = "1"

# Nombre logico -> ruta del JSON dentro de la coleccion de esquemas v1.
# Solo contratos estables. draft/ no se expone.
_V1_SCHEMAS = {
    "manifest": "manifest.schema.json",
    "ledger-event": "ledger-event.schema.json",
}


def _schemas_v1_root() -> Path:
    """Localiza el dir de esquemas v1, funcione instalado o desde el repo.

    - Instalado (wheel): los JSON viajan empaquetados dentro del paquete, en
      zac_contracts/schemas/v1 (via force-include del build).
    - Desde el repo (editable/dev): el canonico vive en schemas/v1 en la raiz
      del repo, un nivel arriba del paquete.
    """
    packaged = Path(str(files("zac_contracts"))) / "schemas" / "v1"
    if packaged.is_dir():
        return packaged
    repo = Path(__file__).resolve().parent.parent / "schemas" / "v1"
    if repo.is_dir():
        return repo
    raise RuntimeError(
        "No se encontraron los esquemas v1 ni empaquetados "
        "(zac_contracts/schemas/v1) ni en el repo (schemas/v1)."
    )


def schema_path(name: str) -> Path:
    """Ruta al JSON de un contrato estable v1 (ej: 'manifest', 'ledger-event')."""
    if name not in _V1_SCHEMAS:
        raise KeyError(
            f"Contrato desconocido: {name!r}. Estables v1: {sorted(_V1_SCHEMAS)}."
        )
    return _schemas_v1_root() / _V1_SCHEMAS[name]


@lru_cache(maxsize=None)
def load_schema(name: str) -> dict:
    """Carga y cachea el JSON Schema de un contrato estable v1 como dict."""
    return json.loads(schema_path(name).read_text(encoding="utf-8"))


@lru_cache(maxsize=None)
def event_types() -> tuple[str, ...]:
    """Enum de event_type, derivado del ledger-event.schema.json empaquetado.

    Fuente de verdad unica: el SDK importa esto en vez de mantener su propia
    copia hardcodeada (D-D). Si el enum del esquema cambia, el SDK lo hereda
    sin editar codigo.
    """
    schema = load_schema("ledger-event")
    return tuple(schema["properties"]["event_type"]["enum"])
