"""quarto_app/services/antes_de_publicar.py — «Antes de publicar» (campo 15 de la norma del flujo de conocimiento), sin Qt:
las órdenes de `escritura/scripts/antes_de_publicar.py`, el mismo motor de controles de «Antes de entregar» de LaTeX
Studio, y lo que la ventana necesita de su respuesta.

Objetivo: que un post salga a la web con la cadena de evidencia de un PDF (C15.1 a C15.8): cifras del paquete de datafw
  con su versión, citas que existen en Zotero y en la biblioteca y cotejadas con su ficha, figuras con texto alternativo,
  la IA declarada, licencia y enlace permanente, y un HTML accesible.
Método: la ventana no revisa nada por su cuenta (como con los backends de `../backend/`): arma la orden con `orden()` y la
  corre en un proceso con `correr()`, que devuelve el JSON del motor. escritura se encuentra por `WRITING_DIR` de
  core/env.py; sin él, `disponible()` es falso y la acción queda apagada con su motivo. `entradas(...)` dice qué posts
  toca una publicación (los `.qmd` y `.md` de los archivos por publicar, por la carpeta de cada entrada).
Fundamento: Haynes et al. (2009, Calibre 11185): la lista al final; el de cada control, en escritura/scripts/entrega/.
Límite: no renderiza; el motor revisa el HTML si ya está renderizado (Ctrl+Mayús+K antes).
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from quarto_app.services import paths

INTERPRETE = "/usr/bin/python3"              # el motor solo necesita PyYAML, que trae el Python del sistema
PLAZO = 120
RENDERIZABLES = (".qmd", ".md")


def escritura_dir() -> Path | None:
    try:
        d = Path(paths.core_env().WRITING_DIR)
    except Exception:                                        # noqa: BLE001  sin core/env.py: no hay motor
        return None
    return d if (d / "scripts" / "antes_de_publicar.py").is_file() else None


def disponible() -> bool:
    return escritura_dir() is not None


def motivo_no_disponible() -> str:
    return "" if disponible() else "No se encontró escritura/scripts/antes_de_publicar.py (WRITING_DIR de core/env.py)."


def orden(sub: str, *args: str, aplicar: bool = False, raiz: str = "") -> list[str]:
    """La orden del motor: `orden("revisar", "<post>")` → [python3, …/antes_de_publicar.py, revisar, <post>]."""
    d = escritura_dir()
    if d is None:
        return []
    argv = [INTERPRETE, str(d / "scripts" / "antes_de_publicar.py")]
    if raiz:
        argv += ["--raiz", raiz]
    return argv + [sub, *args] + (["--aplicar"] if aplicar else [])


def correr(argv: list[str], plazo: int = PLAZO) -> tuple[dict | None, str]:
    """(el JSON que devolvió, "") o (None, por qué no)."""
    if not argv:
        return None, motivo_no_disponible()
    try:
        r = subprocess.run(argv, capture_output=True, text=True, timeout=plazo, cwd=str(Path(argv[1]).parents[1]))
    except (OSError, subprocess.SubprocessError) as e:
        return None, str(e)
    try:
        return json.loads(r.stdout), ""
    except ValueError:
        return None, (r.stderr or r.stdout or f"salió con {r.returncode}").strip().splitlines()[-1][:300]


def post_de(ruta: str) -> str:
    """El post de un documento abierto: la carpeta de su `index.qmd` o el propio `.qmd`/`.md` ("" si no es un documento)."""
    p = Path(ruta or "")
    if p.suffix not in RENDERIZABLES or not p.is_file():
        return ""
    return str(p)


def entradas(sitio: Path, archivos: list[dict]) -> list[str]:
    """Los documentos que toca una publicación: el `index.qmd` de cada carpeta de entrada con un archivo por publicar, y
    cada `.qmd`/`.md` suelto que cambia (sin los que empiezan por `_`, que Quarto no renderiza)."""
    sitio = Path(sitio)
    salida: list[str] = []
    for a in archivos:
        rel = Path(str(a.get("archivo", "")).split(" -> ")[-1])
        if a.get("estado") == "D" or not rel.parts or rel.parts[0].startswith(("_", ".")):
            continue
        ruta = sitio / rel
        candidato = None
        for d in [ruta.parent, *ruta.parent.parents]:
            if d == sitio or not str(d).startswith(str(sitio)):
                break
            if (d / "index.qmd").is_file():
                candidato = d / "index.qmd"
                break
        if candidato is None and ruta.suffix in RENDERIZABLES and not ruta.name.startswith("_") and ruta.is_file():
            candidato = ruta
        if candidato is not None and str(candidato) not in salida:
            salida.append(str(candidato))
    return salida


def veredicto(resumen: dict) -> str:
    if not resumen:
        return ""
    if resumen.get("listo"):
        return "Listo para publicar"
    return f"Faltan {resumen.get('faltan', 0)}"
