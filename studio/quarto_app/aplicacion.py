"""quarto_app/aplicacion.py — arma Quarto Studio: la aplicación (gui_comun.nucleo), los controladores, el registro de
acciones (menú, barra, menú contextual, paleta, atajos) y carga `qml/Main.qml`.

Toda operación existe una sola vez, aquí, en `Acciones`. Las operaciones de los backends son acciones `op.<id>` que
eligen la operación actual (y llevan a su vista); correrla es siempre «Simular» (F5: la simulación de la CLI, el plan
de la ventana o la ejecución de lo que solo lee) o «Aplicar» (Ctrl+Intro, tras confirmar en QML con la orden exacta y,
al publicar, el sitio y su dominio). Lo que necesita un diálogo lo pide a QML por `Interfaz.pedir`. Python no
construye interfaz; la ventana no renderiza ni publica por su cuenta: toda corrida es la CLI de un backend.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from gui_comun.acciones import Acciones, StandardKey
from gui_comun.consola import Consola
from gui_comun.nucleo import Aplicacion
from gui_comun.qt import QObject, Signal, Slot
from gui_comun.tareas import Tareas

from quarto_app import APP_NAME, APP_VERSION, ORG_NAME
from quarto_app.controladores.ajustes import Ajustes
from quarto_app.controladores.espacio import Espacio
from quarto_app.controladores.flujo import Flujo
from quarto_app.controladores.operaciones import Operaciones
from quarto_app.controladores.sitios import Sitios
from quarto_app.services import operaciones as ops
from quarto_app.services import paths

APP_DIR = Path(__file__).resolve().parent
QML_DIR = APP_DIR / "qml"
RECURSOS_DIR = APP_DIR / "recursos"
REPO = paths.REPO
APP_ID = "quarto-studio"
NOMBRE = APP_NAME
DESCRIPCION = ("La familia de blogs Quarto en una ventana de trabajo: el hub y los doce sitios con su estado (al día, con cambios sin render, "
               "con render sin publicar, con problemas) por la regla de la puerta R6; las entradas con su frontmatter y su fila del Excel; "
               "el índice del vault; los índices de contenido. No renderiza ni publica por su cuenta: cada operación es la CLI de un "
               "backend de este repo, que simula con F5 (o muestra su plan) y aplica con Ctrl+Intro tras confirmar; publicar nombra el "
               "sitio y su dominio, porque Netlify despliega con el push.")
ACENTO = "azul"


def datos_lanzador() -> dict:
    return dict(app_id=APP_ID, nombre=NOMBRE, comentario="Render, publicación, metadatos e índices de los blogs Quarto",
                orden=[paths.interprete(), str(APP_DIR.parent / "main.py")], logo_svg=(RECURSOS_DIR / "marca.svg").read_text(encoding="utf-8"),
                acento=ACENTO, categorias="Office;Publishing;", palabras="quarto;blogs;publicar;render;metadatos;yaml;")


class Interfaz(QObject):
    pedir = Signal(str, "QVariantMap")

    @Slot(str)
    def abrir(self, nombre: str) -> None:
        self.pedir.emit(nombre, {})


def construir(app: Aplicacion, cache: Path | None = None, docs_dir: Path | None = None, hub: Path | None = None) -> dict:
    """Crea controladores y acciones, y los expone al QML. Devuelve lo creado (para las pruebas y las capturas)."""
    env = paths.core_env()
    consola = Consola()
    tareas = Tareas(consola)
    interfaz = Interfaz()
    ajustes = Ajustes()
    espacio = Espacio(consola, ajustes)
    sitios = Sitios(espacio, consola, env, cache=cache, docs_dir=docs_dir)
    flujo = Flujo(espacio, sitios, ajustes, consola, hub=hub)
    operaciones = Operaciones(espacio, sitios, flujo, ajustes, consola, tareas, cache=cache)
    acciones = Acciones()
    acciones.estandar(NOMBRE)
    pedir = lambda que, **datos: (lambda *_: interfaz.pedir.emit(que, datos))

    def objetivo() -> str:
        if espacio.vista in ("entradas", "indice", "contenido") and flujo.elementoRuta:
            return flujo.elementoRuta
        return sitios.entrada or sitios.ruta

    # --- Archivo
    acciones.registrar("archivo.abrir", "&Abrir", "document-open", None, "Archivo", habilitada=False, al_disparar=lambda *_: espacio.abrir(objetivo()),
                       descripcion="La entrada, el enlace o el fragmento seleccionado con la aplicación del sistema (también Intro en la tabla)")
    acciones.registrar("archivo.carpeta", "Abrir su &carpeta", "system-file-manager", "Ctrl+Shift+O", "Archivo", habilitada=False,
                       al_disparar=lambda *_: espacio.abrirDolphin(objetivo()), descripcion="La carpeta del sitio o del elemento seleccionado en Dolphin")
    acciones.registrar("archivo.terminal", "Abrir &terminal aquí", "utilities-terminal", "Shift+F4", "Archivo", habilitada=False,
                       al_disparar=lambda *_: espacio.abrirTerminal(objetivo()))
    acciones.registrar("archivo.navegador", "Abrir en el &navegador", "internet-web-browser", None, "Archivo", habilitada=False, al_disparar=sitios.abrirNavegador,
                       descripcion="El dominio del sitio actual (Netlify)")
    acciones.registrar("archivo.copiar", "Copiar &ruta", "edit-copy", "Ctrl+Shift+C", "Archivo", habilitada=False, al_disparar=lambda *_: espacio.copiar(objetivo()))
    acciones.registrar("archivo.excel", "Abrir el &Excel de metadatos", "x-office-spreadsheet", None, "Archivo", al_disparar=flujo.abrirExcel,
                       descripcion="El Excel de metadatos con la aplicación del sistema (LibreOffice Calc)")
    # --- Editar
    acciones.registrar("editar.filtrar", "&Filtrar", "edit-find", StandardKey.Find, "Editar", al_disparar=pedir("filtrar"))
    acciones.registrar("editar.todo", "Seleccionar &todo", "edit-select-all", StandardKey.SelectAll, "Editar", al_disparar=pedir("seleccionar_todo"))
    # --- Ver
    for i, (nombre, texto, icono) in enumerate(ops.VISTAS, start=1):
        acciones.registrar(f"ver.vista.{nombre}", f"&{i} {texto}", icono, f"Ctrl+{i}", "Ver › Vista", marcable=True,
                           al_disparar=lambda *_, n=nombre: espacio.fijarVista(n))
    acciones.registrar("ver.releer", "&Releer", "view-refresh", "F6", "Ver", al_disparar=lambda *_: releer(),
                       descripcion="Vuelve a leer los sitios y su estado, las entradas, el índice o los fragmentos de la vista")
    # --- Sitio y Flujo: elegir cada operación
    for o in ops.OPERACIONES:
        grupo = "Sitio" if o.vista == "sitios" else "Flujo › " + dict((n, t) for n, t, _i in ops.VISTAS)[o.vista]
        acciones.registrar(f"op.{o.id}", o.titulo, "system-run" if o.vista != "sitios" else "folder-html", None, grupo,
                           al_disparar=lambda *_, i=o.id: operaciones.fijar(i), descripcion=o.descripcion)
    acciones.registrar("op.simular", "&Simular", "system-run", StandardKey.Refresh, "Sitio", al_disparar=operaciones.simular,
                       descripcion="Corre la simulación de la CLI o muestra el plan de la ventana; la salida queda en el panel inferior y en la pestaña Plan")
    acciones.registrar("op.aplicar", "&Aplicar…", "dialog-ok-apply", "Ctrl+Return", "Sitio", habilitada=False, al_disparar=pedir("aplicar"),
                       descripcion="Muestra la orden exacta y lo que toca (al publicar, el sitio y su dominio); si confirmas, corre de verdad")
    acciones.registrar("op.cancelar", "&Cancelar la operación", "process-stop", None, "Sitio", habilitada=False, al_disparar=operaciones.cancelar,
                       descripcion="Detiene la corrida en curso (también el preview)")
    acciones.registrar("sitio.nueva_entrada", "&Nueva entrada…", "document-new", StandardKey.New, "Sitio", habilitada=False, al_disparar=pedir("nueva_entrada"),
                       descripcion="Una entrada nueva en el sitio actual con los campos del asistente (APAQuarto)")
    acciones.registrar("sitio.entradas", "Ver sus &entradas", "text-markdown", None, "Sitio", habilitada=False, al_disparar=pedir("pestana", indice=1))
    acciones.registrar("sitio.problemas", "Ver los &problemas del render", "data-warning", None, "Sitio", habilitada=False, al_disparar=pedir("pestana", indice=2))
    # --- Herramientas
    acciones.registrar("herr.lanzador", "Instalar el acceso &directo", "application-x-executable", None, "Herramientas", al_disparar=lambda *_: instalar_lanzador())
    acciones.registrar("herr.venv", "El &entorno del studio…", "python", None, "Herramientas", al_disparar=pedir("venv"),
                       descripcion="Qué intérprete corre los backends de Python y cómo crear el .venv (openpyxl, pandas)")
    # --- Ayuda
    acciones.registrar("ayuda.manual", "&Manual de Quarto Studio", "help-contents", StandardKey.HelpContents, "Ayuda",
                       al_disparar=lambda *_: subprocess.Popen(["xdg-open", str(REPO / "studio" / "README.md")]))
    acciones.registrar("ayuda.backend", "Manual del &backend de la operación", "help-hint", None, "Ayuda", al_disparar=lambda *_: abrir_readme_backend(),
                       descripcion="El README del backend al que pertenece la operación elegida")

    acciones.definir_menus([
        ("&Archivo", ["archivo.abrir", "archivo.carpeta", "archivo.terminal", "archivo.navegador", "archivo.copiar", "|", "archivo.excel", "|", "app.salir"]),
        ("&Editar", ["editar.filtrar", "editar.todo"]),
        ("&Ver", ["ventana.navegacion", "ventana.detalles", "ventana.inferior", "|", ("&Vista", [f"ver.vista.{n}" for n, *_r in ops.VISTAS]), "|",
                  "ver.releer", "|", "ventana.pantalla_completa"]),
        ("&Sitio", ["op.simular", "op.aplicar", "op.cancelar", "|", "sitio.nueva_entrada", "sitio.entradas", "sitio.problemas", "|"]
                   + [f"op.{o.id}" for o in ops.de_vista("sitios")]),
        ("&Flujo", [(f"&{t}", [f"op.{o.id}" for o in ops.de_vista(n)]) for n, t, _i in ops.VISTAS if n != "sitios"]),
        ("&Herramientas", ["herr.lanzador", "herr.venv", "|", "ventana.paleta"]),
        ("A&justes", ["app.ajustes"]),
        ("Ay&uda", ["ayuda.manual", "ayuda.backend", "app.acerca"]),
    ])
    acciones.definir_barra(["op.simular", "op.aplicar", "|", "sitio.nueva_entrada"])
    acciones.anadir_fuente(espacio.entradas_paleta)
    acciones.anadir_fuente(operaciones.entradas_paleta)
    acciones.anadir_fuente(sitios.entradas_paleta)

    def releer() -> None:
        if espacio.vista == "sitios":
            sitios.recargar()
        else:
            flujo.recargar(espacio.vista)

    def instalar_lanzador() -> None:
        if not tareas.activa:
            tareas.proceso("Instalando el acceso directo", ["bash", str(REPO / "install.sh")], cwd=str(REPO))

    def abrir_readme_backend() -> None:
        o = ops.operacion(operaciones.actual)
        if o is None:
            return
        carpeta = {"sitios": "script_blogs_manager", "entradas": "script_metadata_manager", "indice": "script_pub_index_symlink",
                   "contenido": "script_generador_publicacion_similar"}[o.vista]
        if o.id.startswith("yaml_"):
            carpeta = "script_format_yaml"
        subprocess.Popen(["xdg-open", str(REPO / "backend" / carpeta / "README.md")])

    def vista_cambiada():
        for nombre in acciones.nombres():
            if nombre.startswith("ver.vista."):
                acciones.marcar(nombre, nombre == f"ver.vista.{espacio.vista}")
        disponibilidad()

    def disponibilidad():
        activa = tareas.activa
        hay_sitio = sitios.hayActual
        hay_elemento = espacio.vista != "sitios" and bool(flujo.elementoRuta)
        acciones.habilitar("archivo.abrir", hay_elemento or sitios.hayEntrada)
        for nombre in ("archivo.carpeta", "archivo.terminal", "archivo.copiar"):
            acciones.habilitar(nombre, hay_sitio or hay_elemento)
        acciones.habilitar("archivo.navegador", hay_sitio and bool(sitios.dominio))
        acciones.habilitar("sitio.nueva_entrada", hay_sitio and not activa)
        acciones.habilitar("sitio.entradas", hay_sitio)
        acciones.habilitar("sitio.problemas", hay_sitio and sitios.nProblemas > 0)
        a = acciones.accion("op.simular")
        a.texto = f"&{operaciones.verbo}"
        acciones.habilitar("op.simular", operaciones.puedeSimular)
        b = acciones.accion("op.aplicar")
        b.visible = operaciones.escribe
        acciones.habilitar("op.aplicar", operaciones.puedeAplicar)
        acciones.habilitar("op.cancelar", operaciones.enCurso)
        acciones.habilitar("ver.releer", not activa)
        acciones.habilitar("herr.lanzador", not activa)
        acciones.habilitar("ayuda.backend", operaciones.hayOperacion)

    def barra_estado():
        espacio.fijarResumen(sitios.resumen)
        partes = []
        if sitios.hayActual:
            partes.append(f"{sitios.nombre} · {sitios.estadoTexto}")
        if operaciones.hayOperacion:
            partes.append(operaciones.titulo)
        espacio.fijarContexto(" · ".join(partes))

    espacio.vistaCambiada.connect(vista_cambiada)
    sitios.cambiado.connect(lambda: (disponibilidad(), barra_estado()))
    sitios.actualCambiado.connect(lambda: (disponibilidad(), barra_estado()))
    sitios.entradaCambiada.connect(disponibilidad)
    flujo.elementoCambiado.connect(disponibilidad)
    operaciones.cambiado.connect(lambda: (disponibilidad(), barra_estado()))
    tareas.cambiada.connect(disponibilidad)
    vista_cambiada()
    barra_estado()

    piezas = dict(env=env, consola=consola, tareas=tareas, interfaz=interfaz, ajustes=ajustes, espacio=espacio, sitios=sitios, flujo=flujo,
                  operaciones=operaciones, acciones=acciones)
    for nombre, objeto in piezas.items():
        if nombre != "env":
            app.exponer(nombre, objeto)
    app.exponer("descripcionStudio", DESCRIPCION)
    app._piezas = piezas
    return piezas


def relanzar_con_venv(argv: list[str], guion: Path | None = None) -> None:
    """Si existe el .venv del studio y no es el intérprete actual, relanza `guion` (por omisión main.py) con él (rediseño Q7)."""
    venv = paths.venv_dir() / "bin" / "python"
    ya_dentro = Path(sys.prefix).resolve() == paths.venv_dir().resolve()      # el ejecutable del .venv es un enlace al del sistema: se mira el prefijo
    if venv.is_file() and not ya_dentro and not os.environ.get("QUARTO_STUDIO_SIN_VENV"):
        os.execv(str(venv), [str(venv), str(guion or APP_DIR.parent / "main.py"), *argv])


def main(argv: list[str]) -> int:
    relanzar_con_venv(argv)
    if not (paths.venv_dir() / "bin" / "python").is_file():
        print(f"{NOMBRE}: sin el entorno del studio, los backends de Python (metadatos) no tienen openpyxl ni pandas. Créalo con:\n  "
              + paths.orden_crear_venv(), file=sys.stderr)
    from gui_comun import lanzador
    atendido = lanzador.desde_main(argv, **datos_lanzador())
    if atendido is not None:
        return atendido
    app = Aplicacion(APP_ID, NOMBRE, version=APP_VERSION, organizacion=ORG_NAME, nombre_ajustes=APP_NAME)
    construir(app)
    return app.ejecutar(QML_DIR / "Main.qml", humo="--smoke" in argv)
