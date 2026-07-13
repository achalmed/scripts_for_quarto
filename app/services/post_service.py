"""
post_service.py — Creación de posts APAQuarto desde la GUI.

El asistente interactivo de script_blogs_manager/lib/07-post-creator.sh
(~50 prompts encadenados) no puede reutilizarse de forma no interactiva,
así que esta es la ÚNICA lógica portada a Python: genera el mismo
index.qmd (mismo orden de campos y misma plantilla de contenido) a partir
de los datos recogidos en el diálogo NewPostDialog.
"""

from __future__ import annotations

import re
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


def slug(texto: str) -> str:
    """Mismo slug que el script: minúsculas, espacios→guiones, solo [a-z0-9-]."""
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    texto = texto.lower().replace(" ", "-")
    return re.sub(r"[^a-z0-9-]", "", texto)


def _lista_yaml(nombre: str, valores: list[str]) -> str:
    interior = ", ".join(f'"{v.strip()}"' for v in valores if v.strip())
    return f"{nombre}: [{interior}]\n" if interior else ""


def generar_index_qmd(datos: DatosPost) -> str:
    """Construye el frontmatter + cuerpo, replicando 07-post-creator.sh."""
    hoy = date.today().isoformat()
    y: list[str] = ["---\n", f'title: "{datos.titulo}"\n']

    if datos.subtitulo:
        y.append(f'subtitle: "{datos.subtitulo}"\n')
    y.append(f'shorttitle: "{datos.titulo_corto or datos.titulo}"\n')
    y.append(f'date: "{hoy}"\n')
    y.append('date-modified: "today"\n')
    y.append(_lista_yaml("tags", datos.tags))
    y.append(_lista_yaml("categories", datos.categorias))
    y.append("image: ../featured.jpg\n")
    y.append(f"bibliography: {datos.bibliography}\n")
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
        y.append(f'impact-statement: "{datos.impact_statement}"\n')

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
        y.append(f'abstract: "{datos.abstract}"\n')
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
