"""quarto_app/services/render.py — lo que la ventana lee de la salida de `quarto render` (sin Qt; se prueba solo): el
progreso por entrada («[ 3/41] posts/…/index.qmd») para la barra de estado y los problemas (errores y avisos de
Quarto, Pandoc, LaTeX o un motor, con su archivo y su línea cuando los dicen) para la pestaña Problemas. Un sitio se
verifica renderizando (N 5.16); la CLI no deja registro: la ventana lo guarda por sitio."""
from __future__ import annotations

import re

_PROGRESO = re.compile(r"^\[\s*(\d+)/(\d+)\]\s+(\S+)")
_ERROR = re.compile(r"^\s*(?:ERROR|Error|error)\b[:\s]+(.*)")
_AVISO = re.compile(r"^\s*(?:WARN(?:ING)?|Warning|warning)\b[:\s]+(.*)")
_ARCHIVO_LINEA = re.compile(r"([\w./-]+\.(?:qmd|md|yml|yaml|tex|bib|py|R))(?::(\d+))?")
_RUIDO = re.compile(r"^\s*(?:Output created|Rendering|pandoc|\s*$)")


def progreso_de(texto: str) -> tuple | None:
    """`[ 3/41] posts/2025-06-01-x/index.qmd` → (porcentaje, «3 de 41 · index.qmd»)."""
    m = _PROGRESO.match(texto)
    if not m:
        return None
    n, total = int(m.group(1)), int(m.group(2))
    return (int((n - 1) * 100 / total) if total else 0, f"{n} de {total} · {m.group(3)}")


def problemas_de(texto: str) -> list[dict]:
    """Los errores y avisos de una salida de render, uno por línea: nivel, mensaje, archivo, línea."""
    salida = []
    ultimo_archivo = ""
    for linea in texto.splitlines():
        m = _PROGRESO.match(linea)
        if m:
            ultimo_archivo = m.group(3)
            continue
        nivel, mensaje = "", ""
        me, ma = _ERROR.match(linea), _AVISO.match(linea)
        if me:
            nivel, mensaje = "error", me.group(1).strip()
        elif ma:
            nivel, mensaje = "aviso", ma.group(1).strip()
        elif "Undefined control sequence" in linea or "! LaTeX Error" in linea or "Exception" in linea:
            nivel, mensaje = "error", linea.strip()
        if not nivel or _RUIDO.match(mensaje):
            continue
        archivo, numero = "", 0
        mal = _ARCHIVO_LINEA.search(mensaje) or _ARCHIVO_LINEA.search(linea)
        if mal:
            archivo, numero = mal.group(1), int(mal.group(2) or 0)
        salida.append({"nivel": nivel, "mensaje": mensaje or linea.strip(), "archivo": archivo or ultimo_archivo, "linea": numero, "detalle": ""})
    return salida


def resumen_problemas(problemas: list[dict]) -> str:
    e = sum(1 for p in problemas if p["nivel"] == "error")
    a = sum(1 for p in problemas if p["nivel"] == "aviso")
    if not problemas:
        return "sin problemas"
    partes = []
    if e:
        partes.append(f"{e} error" + ("" if e == 1 else "es"))
    if a:
        partes.append(f"{a} aviso" + ("" if a == 1 else "s"))
    return " · ".join(partes)
