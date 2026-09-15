"""backend/script_metadata_manager/lib/fechas.py — normalización de fechas al formato canónico ISO AAAA-MM-DD.

Objetivo: que el campo `date` tenga una sola grafía en los .qmd de la familia
  de blogs y en la columna `date` del Excel: `AAAA-MM-DD`, la de toda fecha del
  ecosistema (meta/NORMATIVA_ARCHIVOS.md §3). Hasta v2.2 el formato canónico
  del gestor era `MM/DD/YYYY`; desde M6 (2026-09-15, v2.3.0) es ISO.
Método: funciones puras, sin dependencias del resto de lib/. Reconocen lo que
  PyYAML y openpyxl devuelven (date, datetime), el `MM/DD/YYYY` heredado, el
  ISO y el ISO con hora (`AAAA-MM-DDTHH:MM:SS+00:00`, que Quarto acepta pero la
  normativa reserva a claves generadas), y devuelven `AAAA-MM-DD`.
Fundamento: NORMATIVA_ARCHIVOS §3 (hallazgo H8 del diagnóstico de metadatos).
Alternativa: seguir con `MM/DD/YYYY` y traducir en el Excel. Se descarta: el
  validador `core/archivos.py` (A05) exige ISO en todo `date`, y Quarto lo lee
  sin ambigüedad de día/mes.
Límite: un valor irreconocible devuelve None y decide el llamador; no se
  inventa una fecha.
"""

import re
from datetime import date, datetime
from typing import Optional

_ISO_RE    = re.compile(r"^(\d{4})-(\d{2})-(\d{2})(?:[T ].*)?$")
_MDY_RE    = re.compile(r"^(\d{2})/(\d{2})/(\d{4})$")
_CARPETA_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})")


def _valida(anio: str, mes: str, dia: str) -> Optional[str]:
    """'2023','05','12' → '2023-05-12'; None si no es una fecha del calendario."""
    try:
        return date(int(anio), int(mes), int(dia)).isoformat()
    except ValueError:
        return None


def fecha_de_carpeta(nombre_carpeta: str) -> Optional[str]:
    """'2023-05-12-titulo' → '2023-05-12'; None si la carpeta no empieza por fecha."""
    m = _CARPETA_RE.match(nombre_carpeta)
    return _valida(*m.groups()) if m else None


def a_iso(valor) -> Optional[str]:
    """Cualquier grafía de fecha admitida → 'AAAA-MM-DD'; None si no se reconoce.

    date(2023,5,12) → '2023-05-12' · '05/12/2023' → '2023-05-12' ·
    '"2021-06-01T10:00:00+00:00"' → '2021-06-01' · '=TEXT(...)' → None
    """
    if valor is None:
        return None
    if isinstance(valor, (date, datetime)):
        return valor.strftime("%Y-%m-%d")
    texto = str(valor).strip().strip("'\"").strip()
    m = _ISO_RE.match(texto)
    if m:
        return _valida(*m.groups())
    m = _MDY_RE.match(texto)
    if m:
        mes, dia, anio = m.groups()
        return _valida(anio, mes, dia)
    return None


def es_iso(valor) -> bool:
    """True solo si el valor ya es exactamente 'AAAA-MM-DD' (sin hora, sin comillas)."""
    if isinstance(valor, date) and not isinstance(valor, datetime):
        return True
    return isinstance(valor, str) and bool(re.match(r"^\d{4}-\d{2}-\d{2}$", valor.strip()))
