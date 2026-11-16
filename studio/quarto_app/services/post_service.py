"""
post_service.py — Creación de posts APAQuarto desde la GUI.

El asistente interactivo de script_blogs_manager/lib/07-post-creator.sh
(~50 prompts encadenados) no puede reutilizarse de forma no interactiva,
así que esta es la ÚNICA lógica portada a Python: genera el mismo
index.qmd (mismo orden de campos y misma plantilla de contenido) a partir
de los datos recogidos en el diálogo NewPostDialog.

También se usa SIN la ventana (2026-11-17, posts desde Qillqa): `python3 post_service.py crear --blog <carpeta del blog>
--datos <json>` crea el mismo post desde otro programa (Yachay, el módulo de escritura de Qillqa). Simula por defecto
(dice qué carpeta y qué `index.qmd` nacerían, sin escribir) y crea con `--aplicar`. Los campos que la ventana no pide
(`descripcion`, `borrador`, `pdf_url`, `csl`, `fuentes`, `cuerpo`) son opcionales: sin ellos el `index.qmd` es el de
siempre, byte a byte. Solo usa la biblioteca estándar de Python: no carga Qt ni `quarto_app`.
"""

from __future__ import annotations

import json
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path


@dataclass
class DatosPost:
    """Respuestas del asistente (equivalentes a los prompts del script Bash)."""

    carpeta_posts: str = "posts"
    titulo: str = ""
    subtitulo: str = ""
    titulo_corto: str = ""
    tags: list[str] = field(default_factory=list)
    categorias: list[str] = field(default_factory=list)
    bibliography: str = "references.bib"

    # Opciones APAQuarto
    floatsintext: bool = False
    numbered_lines: bool = False
    no_ampersand: bool = False
    mask: bool = False
    meta_analysis: bool = False
    impact_statement: str = ""

    # Tipo de documento: jou | man | doc | stu
    doc_type: str = "jou"
    journal: str = ""
    volume: str = ""
    course: str = ""
    professor: str = ""
    duedate: str = ""

    # Formatos de salida
    formato_docx: bool = True
    formato_html: bool = True
    formato_pdf: bool = True
    formato_typst: bool = False

    abstract: str = ""
    keywords: list[str] = field(default_factory=list)
    word_count: bool = False
    lang: str = "es"

    # Lo que un post publicado lleva y la ventana no pide (docs/publicar-un-post.md del hub, §3; Método Documental:
    # `fuentes:` en el frontmatter). Vacío o None: no se escribe.
    descripcion: str = ""             # description: el resumen de la tarjeta (140 a 160 caracteres)
    borrador: bool | None = None      # draft: true o false (el _metadata.yml de la sección ya dice true)
    pdf_url: str = ""                 # citation: {type, author, pdf-url} (sync-pdf-urls solo actualiza uno que exista)
    autor_cita: str = ""              # el autor del bloque citation (sin él, no hay bloque)
    csl: str = ""                     # csl: el APA de apaquarto, relativo al post (sin él, el HTML cita en Chicago)
    fuentes: list[dict] = field(default_factory=list)   # [{calibre_id, zotero, uso}]
    cuerpo: str = ""                  # el cuerpo; vacío, la plantilla de siempre


def slug(texto: str) -> str:
    """Mismo slug que el script: minúsculas, espacios→guiones, solo [a-z0-9-]."""
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    texto = texto.lower().replace(" ", "-")
    return re.sub(r"[^a-z0-9-]", "", texto)


def _escalar(valor: str) -> str:
    """Un texto como escalar YAML entre comillas dobles (con sus comillas y barras escapadas): nunca rompe el bloque."""
    return json.dumps(" ".join(str(valor).split()), ensure_ascii=False)


def _lista_yaml(nombre: str, valores: list[str]) -> str:
    interior = ", ".join(f'"{v.strip()}"' for v in valores if v.strip())
    return f"{nombre}: [{interior}]\n" if interior else ""


def generar_index_qmd(datos: DatosPost) -> str:
    """Construye el frontmatter + cuerpo, replicando 07-post-creator.sh."""
    hoy = date.today().isoformat()
    y: list[str] = ["---\n", f"title: {_escalar(datos.titulo)}\n"]

    if datos.subtitulo:
        y.append(f"subtitle: {_escalar(datos.subtitulo)}\n")
    y.append(f"shorttitle: {_escalar(datos.titulo_corto or datos.titulo)}\n")
    if datos.descripcion:
        y.append(f"description: {_escalar(datos.descripcion)}\n")
    y.append(f'date: "{hoy}"\n')
    y.append('date-modified: "today"\n')
    y.append(_lista_yaml("tags", datos.tags))
    y.append(_lista_yaml("categories", datos.categorias))
    y.append("image: ../featured.jpg\n")
    if datos.borrador is not None:
        y.append(f"draft: {'true' if datos.borrador else 'false'}\n")
    y.append(f"bibliography: {datos.bibliography}\n")
    if datos.csl:
        y.append(f"csl: {datos.csl}\n")
    if datos.pdf_url and datos.autor_cita:
        y.append("citation:\n  type: article-journal\n  author:\n"
                 f"    - {_escalar(datos.autor_cita)}\n  pdf-url: {datos.pdf_url}\n")
    if datos.fuentes:
        y.append("fuentes:\n")
        for f in datos.fuentes:
            y.append("  - {" + ", ".join(f"{k}: {_escalar(str(v)) if not isinstance(v, int) else v}"
                                      for k, v in f.items() if v not in (None, "")) + "}\n")
    y.append("jupyter: python3\n")

    if datos.floatsintext:
        y.append("floatsintext: true\n")
    if datos.numbered_lines:
        y.append("numbered-lines: true\n")
    if datos.no_ampersand:
        y.append("no-ampersand-parenthetical: true\n")
    if datos.mask:
        y.append("mask: true\n")
    if datos.meta_analysis:
        y.append("meta-analysis: true\n")
    if datos.impact_statement:
        y.append(f"impact-statement: {_escalar(datos.impact_statement)}\n")

    if datos.doc_type == "jou":
        if datos.journal:
            y.append(f'journal: "{datos.journal}"\n')
        if datos.volume:
            y.append(f'volume: "{datos.volume}"\n')
    elif datos.doc_type == "stu":
        if datos.course:
            y.append(f'course: "{datos.course}"\n')
        if datos.professor:
            y.append(f'professor: "{datos.professor}"\n')
        if datos.duedate:
            y.append(f'duedate: "{datos.duedate}"\n')

    if datos.abstract:
        y.append(f"abstract: {_escalar(datos.abstract)}\n")
    y.append(_lista_yaml("keywords", datos.keywords))
    if datos.word_count:
        y.append("word-count: true\n")

    y.append(f"lang: {datos.lang}\n")
    if datos.lang != "en":
        y.append(
            "language:\n"
            '  citation-last-author-separator: "y"\n'
            '  citation-masked-author: "Cita Enmascarada"\n'
            '  citation-masked-date: "n.f."\n'
            '  title-block-author-note: "Nota de Autores"\n'
        )

    formatos = []
    if datos.formato_docx:
        formatos.append("apaquarto-docx: default")
    if datos.formato_html:
        formatos.append("apaquarto-html: default")
    if datos.formato_pdf:
        formatos.append(f"apaquarto-pdf:\n    documentmode: {datos.doc_type}")
    if datos.formato_typst:
        formatos.append("apaquarto-typst: default")
    if formatos:
        y.append("format:\n")
        for f in formatos:
            y.append("  " + f.replace("\n", "\n  ") + "\n")

    y.append("---\n")
    if datos.cuerpo.strip():
        return "".join(p for p in y if p) + "\n" + datos.cuerpo.strip("\n") + "\n"
    cuerpo = (
        "\n## Introducción\n\n"
        "Escribe aquí la introducción de tu post...\n\n"
        "## Desarrollo\n\n### Sección 1\n\nContenido...\n\n"
        "### Sección 2\n\nContenido...\n\n"
        "## Conclusiones\n\nEscribe tus conclusiones aquí...\n\n"
        "## Referencias\n\n"
        "Las referencias se generarán automáticamente desde references.bib\n"
    )
    return "".join(p for p in y if p) + cuerpo


def crear_post(blog_dir: Path, datos: DatosPost) -> Path:
    """
    Crea la carpeta YYYY-MM-DD-slug con index.qmd y references.bib.
    Lanza FileExistsError si el post ya existe.
    """
    post_dir = blog_dir / datos.carpeta_posts / f"{date.today().isoformat()}-{slug(datos.titulo)}"
    if post_dir.exists():
        raise FileExistsError(f"Ya existe un post con ese nombre: {post_dir}")
    post_dir.mkdir(parents=True)
    (post_dir / "index.qmd").write_text(generar_index_qmd(datos), encoding="utf-8")
    (post_dir / "references.bib").touch()
    return post_dir


def carpeta_del_post(blog_dir: Path, datos: DatosPost) -> Path:
    """La carpeta que nacería: `<blog>/<sección>/AAAA-MM-DD-slug` (la fecha es la de hoy, como en el asistente)."""
    return Path(blog_dir) / datos.carpeta_posts / f"{date.today().isoformat()}-{slug(datos.titulo)}"


def datos_de(d: dict) -> DatosPost:
    """Un DatosPost desde un diccionario (el JSON de la orden `crear`); una clave desconocida es un error, no se ignora."""
    conocidos = DatosPost.__dataclass_fields__
    malos = sorted(k for k in d if k not in conocidos)
    if malos:
        raise ValueError("Campos desconocidos: " + ", ".join(malos))
    return DatosPost(**d)


def main(argv: list[str] | None = None) -> int:
    """`crear --blog <carpeta> --datos <archivo JSON o -> [--aplicar]`: simula (la carpeta y el index.qmd, en JSON) o crea.
    Sale 0 bien, 1 si el post ya existe o la sección no está, 2 si los datos no sirven."""
    import argparse

    ap = argparse.ArgumentParser(prog="post_service.py", description="Crea un post del blog sin el asistente interactivo.")
    sub = ap.add_subparsers(dest="orden", required=True)
    c = sub.add_parser("crear", help="crear un post (simula salvo --aplicar)")
    c.add_argument("--blog", required=True, help="carpeta del blog (un pub o el hub)")
    c.add_argument("--datos", required=True, help="archivo JSON con los campos de DatosPost, o - para la entrada estándar")
    c.add_argument("--aplicar", action="store_true", help="crear de verdad (sin esto, solo simula)")
    a = ap.parse_args(argv)
    try:
        crudo = sys.stdin.read() if a.datos == "-" else Path(a.datos).read_text(encoding="utf-8")
        datos = datos_de(json.loads(crudo))
        if not datos.titulo.strip():
            raise ValueError("El post necesita un título.")
    except (OSError, ValueError, TypeError) as e:
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        return 2
    blog = Path(a.blog)
    seccion = blog / datos.carpeta_posts
    if not (blog / "_quarto.yml").is_file() or not seccion.is_dir() or ".." in Path(datos.carpeta_posts).parts:
        print(json.dumps({"ok": False, "error": f"No hay un blog con la sección «{datos.carpeta_posts}» en {blog}."}, ensure_ascii=False))
        return 1
    destino = carpeta_del_post(blog, datos)
    texto = generar_index_qmd(datos)
    if destino.exists():
        print(json.dumps({"ok": False, "error": f"Ya existe un post con ese nombre: {destino.name}", "carpeta": str(destino)}, ensure_ascii=False))
        return 1
    if a.aplicar:
        crear_post(blog, datos)
    print(json.dumps({"ok": True, "aplicado": a.aplicar, "carpeta": str(destino), "index_qmd": texto}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
