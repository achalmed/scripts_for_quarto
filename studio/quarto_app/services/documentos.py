"""quarto_app/services/documentos.py — los documentos de un sitio y su página renderizada (reingeniería E3 y E5), sin Qt.

`listar(sitio)`: los archivos que se escriben (`.qmd`, `.md`, `.yml`, `.bib`, `.scss`, `.css`, `.lua`, `.ipynb`) por carpeta,
sin lo generado (`_site`, `_freeze`, `.quarto`) ni los pubs anidados del hub (`_pubs`); cada entrada (`index.qmd` de una
carpeta con fecha) con su título y su fecha. `pagina_de(sitio, documento)`: el HTML que Quarto deja en `_site/` para ese
documento (respeta `output-dir` del `_quarto.yml`). `paginas(sitio)`: las páginas renderizadas, para navegar. Solo lee.
"""
from __future__ import annotations

import re
from pathlib import Path

EXTENSIONES = {".qmd", ".md", ".yml", ".yaml", ".bib", ".scss", ".css", ".lua", ".ipynb", ".json", ".txt"}
OMITIR = {"_site", "_freeze", ".quarto", "_pubs", ".git", "node_modules", "site_libs", "__pycache__", ".venv", "_indice"}
_FECHA = re.compile(r"^(\d{4}-\d{2}-\d{2})-")
_TITULO = re.compile(r'^title:\s*["\']?(.*?)["\']?\s*$', re.M)
_SALIDA = re.compile(r"^\s*output-dir:\s*['\"]?([^'\"\n#]+)", re.M)
TOPE = 3000


def carpeta_salida(sitio: Path) -> Path:
    """`_site` o el `output-dir` que declare el `_quarto.yml`."""
    try:
        m = _SALIDA.search((Path(sitio) / "_quarto.yml").read_text(encoding="utf-8", errors="replace"))
    except OSError:
        m = None
    return Path(sitio) / (m.group(1).strip() if m else "_site")


def _titulo(ruta: Path) -> str:
    try:
        cabeza = ruta.read_text(encoding="utf-8", errors="replace")[:3000]
    except OSError:
        return ""
    if not cabeza.startswith("---"):
        return ""
    m = _TITULO.search(cabeza.split("\n---", 1)[0])
    return m.group(1).strip() if m else ""


def listar(sitio: Path, tope: int = TOPE) -> list[dict]:
    """[{ruta, rel, nombre, carpeta, tipo, titulo, fecha, entrada}] ordenadas por carpeta (las entradas, de la más reciente)."""
    sitio = Path(sitio)
    filas = []
    if not sitio.is_dir():
        return filas
    pila = [sitio]
    while pila and len(filas) < tope:
        d = pila.pop()
        try:
            hijos = sorted(d.iterdir())
        except OSError:
            continue
        for p in hijos:
            if p.name in OMITIR or (p.name.startswith(".") and p.name != ".gitignore"):
                continue
            if p.is_dir() and not p.is_symlink():
                pila.append(p)
            elif p.is_file() and p.suffix.lower() in EXTENSIONES:
                rel = p.relative_to(sitio).as_posix()
                carpeta = str(Path(rel).parent) if Path(rel).parent != Path(".") else ""
                m = _FECHA.match(p.parent.name)
                entrada = p.name == "index.qmd" and bool(m)
                filas.append({"ruta": str(p), "rel": rel, "nombre": p.name, "carpeta": carpeta or "(raíz del sitio)",
                              "tipo": p.suffix.lower().lstrip("."), "titulo": _titulo(p) if p.suffix.lower() in (".qmd", ".md") else "",
                              "fecha": m.group(1) if m else "", "entrada": entrada})
    def clave(f):
        raiz = f["carpeta"] == "(raíz del sitio)"
        return (not raiz, f["carpeta"].split("/")[0], "".join(chr(0x10FFFF - ord(c)) for c in f["carpeta"]) if f["fecha"] else f["carpeta"], f["nombre"])
    filas.sort(key=clave)
    return filas


def pagina_de(sitio: Path, documento: str | Path) -> Path | None:
    """El HTML renderizado de un documento del sitio, si existe (`posts/x/index.qmd` → `_site/posts/x/index.html`)."""
    sitio, doc = Path(sitio), Path(documento)
    try:
        rel = doc.resolve().relative_to(sitio.resolve()) if doc.is_absolute() else doc
    except ValueError:
        return None
    if rel.suffix.lower() not in (".qmd", ".md", ".ipynb"):
        return None
    html = carpeta_salida(sitio) / rel.with_suffix(".html")
    return html if html.is_file() else None


def paginas(sitio: Path, tope: int = 500) -> list[dict]:
    """[{rel, ruta}] de las páginas HTML renderizadas (sin `site_libs`), la portada primero."""
    salida_dir = carpeta_salida(sitio)
    if not salida_dir.is_dir():
        return []
    filas = []
    for p in sorted(salida_dir.rglob("*.html")):
        rel = p.relative_to(salida_dir).as_posix()
        if rel.startswith("site_libs/") or "/site_libs/" in rel:
            continue
        filas.append({"rel": rel, "ruta": str(p)})
        if len(filas) >= tope:
            break
    filas.sort(key=lambda f: (f["rel"] != "index.html", f["rel"]))
    return filas
