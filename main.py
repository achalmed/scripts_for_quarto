#!/usr/bin/env python3
"""
main.py — Punto de entrada de Quarto Studio.

Solo orquesta: crea la QApplication, aplica el tema persistido y muestra
la ventana principal. Toda la lógica vive en app/.
"""

import sys
from pathlib import Path

# Asegurar que el paquete app/ sea importable ejecutando desde cualquier lugar
sys.path.insert(0, str(Path(__file__).parent))

from app.application import crear_aplicacion
from app.ui.main_window import MainWindow


def main() -> int:
    app = crear_aplicacion(sys.argv)
    ventana = MainWindow()
    ventana.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
