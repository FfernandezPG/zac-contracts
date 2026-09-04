"""zac-contracts: binding Python de los contratos versionados de Zac.

El JSON versionado (schemas/) es el artefacto canonico language-agnostic.
Este paquete lo empaqueta y lo entrega a los consumidores Python.
"""
from .loader import (  # noqa: F401
    CONTRACTS_VERSION,
    event_types,
    load_schema,
    schema_path,
)

__all__ = ["CONTRACTS_VERSION", "event_types", "load_schema", "schema_path"]
