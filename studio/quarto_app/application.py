"""
application.py — Creación de la QApplication, iconos y tema (el diseño común de gui_comun, acento azul).
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QFile, QIODevice, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from gui_comun.diseno import Disenador, icono_svg, logo, preparar_plataforma
from gui_comun.theming import aplicar_tema as _aplicar_tema_comun

from quarto_app import APP_NAME, APP_VERSION, ORG_DOMAIN, ORG_NAME
from quarto_app.services import paths
from quarto_app.settings import settings

# Los recursos compilados (resources_rc) registran :/icons.
# Si no están compilados, se cargan directamente del sistema de archivos.
try:
    from quarto_app.resources import resources_rc  # noqa: F401
    _QRC_DISPONIBLE = True
except ImportError:
    _QRC_DISPONIBLE = False


ACENTO = "azul"


def crear_aplicacion(argv: list[str]) -> QApplication:
    preparar_plataforma()                 # sin el plugin de Wayland, XWayland sin aviso
    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    app = QApplication(argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName(ORG_NAME)
    app.setOrganizationDomain(ORG_DOMAIN)
    aplicar_tema(settings().get("general/tema"))
    app.setWindowIcon(QIcon(logo(svg_icono("quarto-studio"), 64)))
    return app


def svg_icono(nombre: str) -> str:
    """El texto SVG de un icono: de los recursos Qt (:/icons) o del disco."""
    if _QRC_DISPONIBLE:
        f = QFile(f":/icons/{nombre}.svg")
        if f.open(QIODevice.ReadOnly):
            texto = bytes(f.readAll()).decode()
            f.close()
            return texto
    ruta = Path(paths.icono(nombre))
    return ruta.read_text(encoding="utf-8") if ruta.is_file() else ""


def icono_app(nombre: str) -> QIcon:
    """Icono SVG que se repinta con el tema (gui_comun.diseno)."""
    texto = svg_icono(nombre)
    return icono_svg(texto) if texto else QIcon()


def aplicar_tema(nombre: str) -> Disenador:
    """El diseño común de los studios (gui_comun.diseno) con el acento de Quarto Studio: sistema · claro · oscuro."""
    disenador = _aplicar_tema_comun(QApplication.instance(), nombre, acento=ACENTO)
    settings().set("general/tema", disenador.modo)
    return disenador
