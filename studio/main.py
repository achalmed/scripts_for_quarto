#!/usr/bin/python3
"""
main.py — Punto de entrada de Quarto Studio. Sin lógica: la aplicación se arma en quarto_app/aplicacion.py.

Corre con el Python del sistema (/usr/bin/python3), cuyo Qt es el que trae Kirigami; si existe el entorno del studio
(`<repo>/.venv`, creado con `/usr/bin/python3 -m venv --system-site-packages .venv` más `pip install openpyxl pandas pyyaml`),
se relanza con él: ve el mismo PySide6 del sistema y además lo que los backends de metadatos necesitan. Sin el .venv
avisa qué crear y sigue. Cada operación es la CLI de un backend de este repo; la ventana no renderiza ni publica por su
cuenta.

Uso:
    /usr/bin/python3 studio/main.py                       # desde quarto-studio/
    /usr/bin/python3 studio/main.py --smoke               # construye la interfaz y sale (prueba de humo)
    /usr/bin/python3 studio/main.py --instalar-lanzador   # el acceso directo del menú (-n simula)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))      # el paquete del studio

from quarto_app.aplicacion import main                          # noqa: E402  (quarto_app localiza gui_comun al importarse)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
