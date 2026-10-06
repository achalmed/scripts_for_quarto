"""
application.py — Creación de la QApplication y gestión del tema claro/oscuro.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from app import APP_NAME, APP_VERSION, ORG_DOMAIN, ORG_NAME
from app.services import paths
from app.settings import settings

# Los recursos compilados (resources_rc) registran :/icons y :/themes.
# Si no están compilados, se cargan directamente del sistema de archivos.
try:
    from app.resources import resources_rc  # noqa: F401
    _QRC_DISPONIBLE = True
except ImportError:
    _QRC_DISPONIBLE = False


def crear_aplicacion(argv: list[str]) -> QApplication:
    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    app = QApplication(argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName(ORG_NAME)
    app.setOrganizationDomain(ORG_DOMAIN)
    app.setWindowIcon(icono_app("quarto-studio"))
    aplicar_tema(settings().get("general/tema"))
    return app


def icono_app(nombre: str) -> QIcon:
    """Icono SVG desde recursos Qt (:/icons) o desde disco como fallback."""
    if _QRC_DISPONIBLE:
        icono = QIcon(f":/icons/{nombre}.svg")
        if not icono.isNull():
            return icono
    return QIcon(paths.icono(nombre))


def aplicar_tema(nombre: str) -> None:
    """Aplica la hoja de estilos claro/oscuro a toda la aplicación."""
    nombre = nombre if nombre in ("claro", "oscuro") else "oscuro"
    qss = ""
    if _QRC_DISPONIBLE:
        from PySide6.QtCore import QFile, QIODevice
        f = QFile(f":/themes/{nombre}.qss")
        if f.open(QIODevice.ReadOnly):
            qss = bytes(f.readAll()).decode()
            f.close()
    if not qss:
        archivo = paths.tema_qss(nombre)
        if archivo.is_file():
            qss = archivo.read_text(encoding="utf-8")
    QApplication.instance().setStyleSheet(qss)
    settings().set("general/tema", nombre)
