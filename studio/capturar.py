#!/usr/bin/python3
"""studio/capturar.py — una captura de Quarto Studio para la documentación sobre la FAMILIA DE SITIOS DE MUESTRA
(`muestra.py`: un hub y tres pubs de juguete con git y remotos «bare» locales, nunca `web` ni los pubs reales) creada en
una carpeta temporal fuera de la carpeta de inicio, con HOME, configuración, caché y estado temporales (ninguna ruta
de la máquina en pantalla), el esquema de color que se pida (con el tema de Kvantum a juego), el área, el proyecto, el
documento abierto, la vista de Herramientas, la operación y, si se pide, la paleta de órdenes. Nada se publica.

    /usr/bin/python3 studio/capturar.py docs/figuras/quarto-studio-claro.png --esquema ~/Documents/lliphi/generado/esquema/LliphiClaro.colors --sitio axiomata --documento matrices
    /usr/bin/python3 studio/capturar.py docs/figuras/quarto-studio-publicacion.png --area publicacion --sitio chaska
    /usr/bin/python3 studio/capturar.py salida.png --area herramientas --vista sitios --operacion render --pestana 3
    /usr/bin/python3 studio/capturar.py salida.png --paleta "publicar"

Antes de capturar corre de verdad, sobre la muestra, «Verificar» del sitio elegido (`main.sh check`, solo lee) y, con
`--render`, un `quarto render` real del sitio (si `quarto` está instalado): la salida del panel inferior y los
problemas son los de la CLI.
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))


def main() -> int:
    parser = argparse.ArgumentParser(description="Captura de Quarto Studio sobre la familia de sitios de muestra")
    parser.add_argument("salida")
    parser.add_argument("--esquema", help="archivo .colors de KDE (relanza con XDG_CONFIG_HOME temporal)")
    parser.add_argument("--area", default="escribir", help="escribir · metadatos · publicacion · herramientas")
    parser.add_argument("--sitio", default="axiomata", help="el proyecto elegido (aequilibria · axiomata · chaska · web)")
    parser.add_argument("--documento", default="", help="abre en el editor el documento del proyecto cuya ruta contenga este texto")
    parser.add_argument("--vista", default="sitios", help="en Herramientas: sitios · entradas · indice · contenido")
    parser.add_argument("--operacion", default="", help="la operación elegida (id del catálogo)")
    parser.add_argument("--fila", type=int, default=-1, help="en Metadatos, la entrada elegida (−1 ninguna)")
    parser.add_argument("--pestana", type=int, default=-1, help="en Herramientas, el lado (0 Resumen · 1 Entradas · 2 Problemas · 3 Operación · 4 Plan · 5 Salida)")
    parser.add_argument("--render", action="store_true", help="renderiza de verdad el sitio de la fila (quarto) antes de capturar")
    parser.add_argument("--sin-correr", action="store_true", help="no corre ninguna operación antes de capturar")
    parser.add_argument("--paleta", default=None, help="abre la paleta de órdenes con este texto")
    parser.add_argument("--ancho", type=int, default=1440)
    parser.add_argument("--alto", type=int, default=900)
    args = parser.parse_args()

    if "QUARTO_STUDIO_CAPTURA" not in os.environ:      # primera pasada: la muestra, el entorno temporal (y esquema), y relanzar
        from quarto_app import aplicacion
        aplicacion.relanzar_con_venv(sys.argv[1:], guion=Path(__file__))   # con el .venv la muestra lleva Excel (openpyxl)
        from gui_comun.galeria.esquema import entorno_con_esquema
        import muestra
        carpeta = Path(tempfile.mkdtemp(prefix="quarto-studio-captura-", dir="/tmp"))   # fuera de la carpeta de inicio
        m = muestra.crear(carpeta / "muestra")
        hogar = Path(m.entorno["HOME"])
        (hogar / ".config").mkdir(parents=True, exist_ok=True)
        config_usuario = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
        for nombre in ("kdeglobals", "kcminputrc", "Kvantum", "fontconfig"):
            origen = config_usuario / nombre
            if origen.is_dir():
                shutil.copytree(origen, hogar / ".config" / nombre, dirs_exist_ok=True)
            elif origen.is_file():
                shutil.copy2(origen, hogar / ".config" / nombre)
        env = entorno_con_esquema(Path(args.esquema).expanduser(), hogar / ".config") if args.esquema else dict(os.environ, XDG_CONFIG_HOME=str(hogar / ".config"))
        if args.esquema:
            # con QApplication (gui-comun 3.0) los campos los pinta el QStyle (Kvantum) con la paleta de su tema: a juego
            tema, kv = Path(args.esquema).stem, hogar / ".config" / "Kvantum"
            if (kv / tema).is_dir():
                (kv / "kvantum.kvconfig").write_text(f"[General]\ntheme={tema}\n", encoding="utf-8")
        env.update(m.entorno)
        env.update({"XDG_DATA_HOME": str(Path.home() / ".local" / "share"), "QUARTO_STUDIO_CAPTURA": str(carpeta), "QT_QPA_PLATFORM": "offscreen",
                    "QUARTO_STUDIO_EXCEL": str(m.excel or "")})
        env.pop("QUARTO_STUDIO_SIN_VENV", None)
        env.setdefault("QT_QPA_PLATFORMTHEME", "kde")
        orden = [sys.executable, str(AQUI / "capturar.py")] + [a for a in sys.argv[1:] if not a.startswith("--esquema") and a != args.esquema]
        codigo = subprocess.run(orden, env=env).returncode
        shutil.rmtree(carpeta, ignore_errors=True)
        return codigo

    from quarto_app import aplicacion
    from gui_comun.nucleo import Aplicacion
    from gui_comun.qt import QTimer

    app = Aplicacion(aplicacion.APP_ID, aplicacion.NOMBRE, version=aplicacion.APP_VERSION, organizacion=aplicacion.ORG_NAME, nombre_ajustes=aplicacion.APP_NAME)
    piezas = aplicacion.construir(app)
    espacio, sitios, operaciones, tareas, interfaz, ajustes, flujo = (piezas[k] for k in ("espacio", "sitios", "operaciones", "tareas", "interfaz", "ajustes", "flujo"))
    if os.environ.get("QUARTO_STUDIO_EXCEL"):
        ajustes.excel = os.environ["QUARTO_STUDIO_EXCEL"]
        flujo.recargar("entradas")
    if not app.cargar(aplicacion.QML_DIR / "Main.qml"):
        return 1
    raiz = app.motor.rootObjects()[0]
    raiz.setProperty("width", args.ancho)
    raiz.setProperty("height", args.alto)

    espacio.fijarVista("sitios")
    espacio.fijarFiltro("todos")
    sitio = args.sitio if args.sitio in sitios.nombres else ""
    pendientes = []
    if not args.sin_correr and sitio:
        pendientes.append(("verificar", False))
        if args.render and shutil.which("quarto"):
            pendientes.append(("render", True))

    def correr_siguiente():
        if tareas.activa:
            QTimer.singleShot(150, correr_siguiente)
            return
        if pendientes:
            id_, aplicar = pendientes.pop(0)
            sitios.irA(sitio)
            operaciones.fijar(id_)
            if aplicar:
                operaciones.aplicar()
            else:
                operaciones.simular()
            QTimer.singleShot(150, correr_siguiente)
            return
        QTimer.singleShot(300, listo)

    def listo():
        espacio.fijarVista(args.vista)
        if sitio:
            sitios.irA(sitio)
        if args.operacion:
            operaciones.fijar(args.operacion)
        espacio.fijarArea(args.area)
        if args.documento:
            d = piezas["documentos"]
            ruta = next((d._filas.fila(i)["ruta"] for i in range(d._filas.filas) if args.documento in d._filas.fila(i)["rel"]), "")
            if ruta:
                interfaz.pedir.emit("editar", {"ruta": ruta})
        if args.fila >= 0:
            piezas["metadatos"].fijarFila(args.fila)
        if args.pestana >= 0:
            QTimer.singleShot(600, lambda: interfaz.pedir.emit("pestana", {"indice": args.pestana}))
        if args.paleta is not None:
            QTimer.singleShot(900, lambda: interfaz.pedir.emit("paleta", {"texto": args.paleta}))
        app.capturar(args.salida, espera_ms=3500)

    QTimer.singleShot(400, correr_siguiente)
    codigo = app.app.exec()
    app.cerrar()
    print("CAPTURA", args.salida)
    return codigo


if __name__ == "__main__":
    sys.exit(main())
