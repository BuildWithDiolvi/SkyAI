"""Guarda las ubicaciones favoritas de SkyAI solo en esta computadora."""

import json
from pathlib import Path


ARCHIVO_FAVORITOS = Path(__file__).resolve().parent / "favoritos_skyai.json"


def cargar_favoritos() -> list[str]:
    if not ARCHIVO_FAVORITOS.exists():
        return []
    try:
        datos = json.loads(ARCHIVO_FAVORITOS.read_text(encoding="utf-8"))
        return datos if isinstance(datos, list) else []
    except (OSError, json.JSONDecodeError):
        return []


def guardar_favoritos(favoritos: list[str]) -> None:
    ARCHIVO_FAVORITOS.write_text(
        json.dumps(favoritos, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def nombre_corto(opcion: str) -> str:
    """Convierte una etiqueta larga del selector en texto agradable para un botón."""
    return opcion.replace("Provincia · ", "").replace("Municipio · ", "")
