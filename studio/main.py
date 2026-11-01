#!/usr/bin/env python3
"""
main.py — Punto de entrada de Quarto Studio.

Solo orquesta: crea la QApplication, aplica el tema persistido y muestra
la ventana principal. Toda la lógica vive en quarto_app/; los backends, en ../backend/ (este mismo repo).

Uso:
    python3 studio/main.py            # desde quarto-studio/
    python3 studio/main.py --smoke    # construye la UI y sale (prueba de humo)
"""

import sys
from pathlib import Path

# El paquete quarto_app importable desde cualquier carpeta (él mismo encuentra gui_comun)
_AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(_AQUI))

from quarto_app.application import crear_aplicacion
from quarto_app.ui.main_window import MainWindow


APP_ID = "quarto-studio"


def datos_lanzador() -> dict:
    """El acceso directo en el menú de aplicaciones (gui_comun.lanzador)."""
    from quarto_app.application import ACENTO, svg_icono
    return dict(app_id=APP_ID, nombre="Quarto Studio", comentario="Render, publicación, metadatos e índices de los blogs Quarto",
                orden=[sys.executable, str(_AQUI / "main.py")], logo_svg=svg_icono("quarto-studio"), acento=ACENTO,
                categorias="Development;Office;", palabras="quarto;blogs;publicar;render;metadatos;yaml;")


def main() -> int:
    from gui_comun import lanzador
    atendido = lanzador.desde_main(sys.argv[1:], **datos_lanzador())   # --instalar-lanzador / --quitar-lanzador
    if atendido is not None:
        return atendido
    app = crear_aplicacion(sys.argv)
    ventana = MainWindow()
    ventana.show()
    if "--smoke" in sys.argv:
        from PySide6.QtCore import QTimer
        QTimer.singleShot(0, ventana.close)   # closeEvent espera al escaneo; la app sale con la última ventana
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
