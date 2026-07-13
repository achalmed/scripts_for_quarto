"""
blog.py — Modelo de dominio: un proyecto de blog Quarto (pub_* o website).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Post:
    """Una publicación (carpeta YYYY-MM-DD-titulo con index.qmd)."""

    ruta: Path
    titulo: str = ""
    fecha: str = ""          # YYYY-MM-DD extraído del nombre de carpeta

    @property
    def nombre(self) -> str:
        return self.ruta.name


@dataclass
class Blog:
    """Un proyecto Quarto gestionable (pub_* o website-achalma)."""

    ruta: Path
    posts: list[Post] = field(default_factory=list)
    tiene_git: bool = False
    tiene_quarto_yml: bool = False

    @property
    def nombre(self) -> str:
        return self.ruta.name

    @property
    def es_website(self) -> bool:
        return not self.nombre.startswith("pub_")

    @property
    def num_posts(self) -> int:
        return len(self.posts)
