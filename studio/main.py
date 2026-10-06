#!/usr/bin/env python3
"""
main.py — Punto de entrada de Quarto Studio.

Solo orquesta: crea la QApplication, aplica el tema persistido y muestra
la ventana principal. Toda la lógica vive en quarto_app/; los backends, en
SCRIPTS_QUARTO/backend/ (core/env).

Uso:
    python3 quarto/main.py            # desde studios/
    python3 quarto/main.py --smoke    # construye la UI y sale (prueba de humo)
"""

import sys
from pathlib import Path

# El paquete quarto_app y el paquete comun de studios/ importables desde cualquier carpeta
_AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(_AQUI))
sys.path.insert(1, str(_AQUI.parent))

from quarto_app.application import crear_aplicacion
from quarto_app.ui.main_window import MainWindow


def main() -> int:
    app = crear_aplicacion(sys.argv)
    ventana = MainWindow()
    ventana.show()
    if "--smoke" in sys.argv:
        from PySide6.QtCore import QTimer
        QTimer.singleShot(0, ventana.close)   # closeEvent espera al escaneo; la app sale con la última ventana
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
