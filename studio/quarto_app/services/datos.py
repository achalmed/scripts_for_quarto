"""quarto_app/services/datos.py — lo que las vistas listan, leído tal cual de donde vive (sin Qt; se prueba solo): las
entradas de cada sitio (`project_scanner`) con su frontmatter, el Excel de metadatos (`openpyxl` del `.venv`; sin él,
la columna queda vacía y se dice), los enlaces por año de `web/_indice/` y los fragmentos `_contenido_*.qmd`. Nada se
escribe."""
from __future__ import annotations

import os
import re
from pathlib import Path

from quarto_app.models.blog import Blog, Post
from quarto_app.services import paths
from quarto_app.services.project_scanner import IGNORAR_DIRS

_FRONTMATTER = re.compile(r"\A---\n(.*?)\n---", re.S)
PREFIJO_HISTORICO = "pub_"


def frontmatter(index_qmd: Path) -> dict:
    """El frontmatter YAML de una entrada (PyYAML si está; si no, las claves de primer nivel a mano)."""
    try:
        texto = index_qmd.read_text(encoding="utf-8", errors="replace")[:6000]
    except OSError:
        return {}
    m = _FRONTMATTER.match(texto)
    if not m:
        return {}
    try:
        import yaml
        d = yaml.safe_load(m.group(1))
        return d if isinstance(d, dict) else {}
    except Exception:          # noqa: BLE001  un YAML raro no tumba la tabla
        d = {}
        for linea in m.group(1).splitlines():
            if linea and not linea.startswith(" ") and ":" in linea:
                k, _, v = linea.partition(":")
                d[k.strip()] = v.strip()
        return d


def _tags(fm: dict) -> str:
    t = fm.get("tags")
    if isinstance(t, list):
        return ", ".join(str(x) for x in t)
    return str(t or "")


def ruta_relativa(blog: Blog, post: Post) -> str:
    """`<carpeta del sitio>/<ruta del index.qmd>`: la forma en que el Excel nombra una entrada (con o sin `pub_`)."""
    return f"{blog.nombre}/{(post.ruta / 'index.qmd').relative_to(blog.ruta).as_posix()}"


def entradas(blogs: list[Blog], en_excel: set[str] | None = None) -> list[dict]:
    """Todas las entradas de todos los sitios, la más reciente primero."""
    filas = []
    for b in blogs:
        for p in b.posts:
            fm = frontmatter(p.ruta / "index.qmd")
            rel = ruta_relativa(b, p)
            filas.append({"fecha": p.fecha, "titulo": p.titulo or str(fm.get("title") or p.nombre), "sitio": b.nombre, "carpeta": p.ruta.name,
                          "tags": _tags(fm), "excel": ("sí" if rel in en_excel else "no") if en_excel is not None else "—",
                          "ruta": str(p.ruta / "index.qmd"), "ruta_relativa": rel, "seccion": p.ruta.parent.name, "frontmatter": fm})
    filas.sort(key=lambda f: f["fecha"], reverse=True)
    return filas


# ------------------------------------------------------------------------------------------------ el Excel
def hay_openpyxl() -> bool:
    import importlib.util
    return importlib.util.find_spec("openpyxl") is not None


def _normalizar_ruta(texto: str) -> str:
    texto = (texto or "").strip().replace("\\", "/")
    return texto[len(PREFIJO_HISTORICO):] if texto.startswith(PREFIJO_HISTORICO) else texto


def leer_excel(ruta: Path | None = None, hoja: str = "METADATOS") -> dict[str, dict]:
    """{ruta relativa de la entrada: su fila} de la hoja de metadatos; vacío sin `openpyxl` o sin el archivo."""
    ruta = Path(ruta) if ruta else paths.excel_por_defecto()
    if not ruta.is_file() or not hay_openpyxl():
        return {}
    import openpyxl
    try:
        libro = openpyxl.load_workbook(ruta, read_only=True, data_only=True)
    except Exception:          # noqa: BLE001
        return {}
    try:
        ws = libro[hoja] if hoja in libro.sheetnames else libro.worksheets[-1]
        filas = ws.iter_rows(values_only=True)
        cabecera = [str(c or "") for c in next(filas, [])]
        if "ruta_archivo" not in cabecera:
            return {}
        i = cabecera.index("ruta_archivo")
        salida = {}
        for fila in filas:
            if fila is None or i >= len(fila) or not fila[i]:
                continue
            salida[_normalizar_ruta(str(fila[i]))] = {k: ("" if v is None else v) for k, v in zip(cabecera, fila) if k}
        return salida
    finally:
        libro.close()


def comparar(fm: dict, fila_excel: dict) -> list[dict]:
    """[{campo, archivo, excel, difiere}] con los campos que el Excel y el frontmatter comparten."""
    salida = []
    for campo, valor in fila_excel.items():
        if campo in ("ruta_archivo", "blog_nombre", "tipo_documento") or campo.startswith("citation_") or campo.startswith("links_"):
            continue
        en_archivo = fm.get(campo)
        a = ", ".join(str(x) for x in en_archivo) if isinstance(en_archivo, list) else ("" if en_archivo is None else str(en_archivo))
        e = "" if valor is None else str(valor)
        if a == "" and e == "":
            continue
        salida.append({"campo": campo, "archivo": a, "excel": e, "difiere": a.strip() != e.strip()})
    return salida


# ------------------------------------------------------------------------------------------- el índice del vault
def enlaces_indice(carpeta: Path | None = None, docs: Path | None = None) -> list[dict]:
    """Los enlaces de `web/_indice/<año>/`: año, nombre, destino (relativo a la raíz del espacio de trabajo si cae
    dentro) y si está roto."""
    carpeta = Path(carpeta) if carpeta else paths.indice_dir()
    docs = str(Path(docs) if docs else paths.detectar_docs_dir()).rstrip("/") + "/"
    filas = []
    if not carpeta.is_dir():
        return filas
    for anio in sorted((p for p in carpeta.iterdir() if p.is_dir()), key=lambda p: p.name, reverse=True):
        for enlace in sorted(anio.iterdir()):
            if not enlace.is_symlink():
                continue
            try:
                destino = os.readlink(enlace)
            except OSError:
                destino = ""
            roto = not enlace.exists()
            if destino.startswith(docs):
                destino = destino[len(docs):]
            filas.append({"anio": anio.name, "enlace": enlace.name, "destino": destino, "estado": "roto" if roto else "bien",
                          "nivel": "negativo" if roto else "positivo", "ruta": str(enlace)})
    return filas


# --------------------------------------------------------------------------------------- fragmentos de contenido
def fragmentos(blogs: list[Blog]) -> list[dict]:
    """Los `_contenido_*.qmd` de cada sitio: subblog, cuántas entradas enlaza, cuándo se modificó."""
    filas = []
    for b in blogs:
        for p in sorted(b.ruta.glob("*/_contenido_*.qmd")) + sorted(b.ruta.glob("_contenido_*.qmd")):
            if any(x in IGNORAR_DIRS for x in p.relative_to(b.ruta).parts):
                continue
            try:
                texto = p.read_text(encoding="utf-8", errors="replace")
                mtime = p.stat().st_mtime
            except OSError:
                continue
            enlaces = len(re.findall(r"\]\(", texto))
            from datetime import datetime
            filas.append({"sitio": b.nombre, "subblog": p.parent.name if p.parent != b.ruta else "(raíz)", "fragmento": p.name,
                          "entradas": str(enlaces), "modificado": datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M"),
                          "ruta": str(p), "crudo": {"entradas": enlaces, "modificado": mtime}})
    return filas
