"""
main_window.py — Ventana principal de Quarto Studio.

Estructura (estilo Qt Creator / VS Code):
  - Barra de menú y barra de herramientas
  - Sidebar de navegación | páginas apiladas
  - Panel inferior con pestañas: Consola y Logs
  - Explorador de proyectos como dock lateral derecho
  - Barra de estado con progreso y tiempo
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QLabel, QMainWindow, QMessageBox, QProgressBar, QSplitter, QStackedWidget,
    QStatusBar, QTabWidget, QToolBar, QWidget, QHBoxLayout, QDockWidget,
)

from app import APP_NAME, APP_VERSION
from app.application import aplicar_tema, icono_app
from app.controllers.blogs_controller import BlogsController
from app.controllers.main_controller import MainController
from app.controllers.metadata_controller import MetadataController
from app.controllers.tools_controller import ToolsController
from app.dialogs.preferences_dialog import PreferencesDialog
from app.settings import settings
from app.ui.pages.blogs_page import BlogsPage
from app.ui.pages.dashboard_page import DashboardPage
from app.ui.pages.index_page import IndexPage
from app.ui.pages.metadata_page import MetadataPage
from app.ui.pages.similar_page import SimilarPage
from app.ui.pages.yaml_page import YamlPage
from app.widgets.console_widget import ConsoleWidget
from app.widgets.file_explorer import FileExplorer
from app.widgets.log_panel import LogPanel
from app.widgets.sidebar import Sidebar


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} {APP_VERSION}")
        self.resize(1280, 820)

        # --- Controladores ------------------------------------------------------
        self.ctl = MainController(self)
        self.ctl_blogs = BlogsController(self.ctl, self)
        self.ctl_metadata = MetadataController(self.ctl, self)
        self.ctl_tools = ToolsController(self.ctl, self)

        # --- Páginas --------------------------------------------------------------
        self.pagina_dashboard = DashboardPage()
        self.pagina_blogs = BlogsPage(self.ctl_blogs)
        self.pagina_metadata = MetadataPage(self.ctl_metadata)
        self.pagina_yaml = YamlPage(self.ctl_tools)
        self.pagina_indices = IndexPage(self.ctl_tools)
        self.pagina_similares = SimilarPage(self.ctl_tools)

        self._paginas = QStackedWidget()
        self._indice_paginas: dict[str, int] = {}
        for id_, pagina in [
            ("dashboard", self.pagina_dashboard),
            ("blogs", self.pagina_blogs),
            ("metadata", self.pagina_metadata),
            ("yaml", self.pagina_yaml),
            ("indices", self.pagina_indices),
            ("similares", self.pagina_similares),
        ]:
            self._indice_paginas[id_] = self._paginas.addWidget(pagina)

        # --- Sidebar + páginas -------------------------------------------------------
        self._sidebar = Sidebar()
        self._sidebar.seccion_cambiada.connect(self._cambiar_pagina)
        self.pagina_dashboard.ir_a_seccion.connect(self._sidebar.seleccionar)

        zona_central = QWidget()
        layout_central = QHBoxLayout(zona_central)
        layout_central.setContentsMargins(0, 0, 0, 0)
        layout_central.setSpacing(0)
        layout_central.addWidget(self._sidebar)
        layout_central.addWidget(self._paginas, stretch=1)

        # --- Panel inferior: consola + logs ---------------------------------------------
        self.consola = ConsoleWidget()
        self.logs = LogPanel()
        panel_inferior = QTabWidget()
        panel_inferior.addTab(self.consola, icono_app("consola"), "Consola")
        panel_inferior.addTab(self.logs, icono_app("logs"), "Logs")

        divisor = QSplitter(Qt.Vertical)
        divisor.addWidget(zona_central)
        divisor.addWidget(panel_inferior)
        divisor.setStretchFactor(0, 3)
        divisor.setStretchFactor(1, 1)
        divisor.setSizes([560, 240])
        self.setCentralWidget(divisor)

        # --- Explorador de proyectos (dock) -------------------------------------------
        self.explorador = FileExplorer()
        dock = QDockWidget("Explorador de proyectos", self)
        dock.setObjectName("dockExplorador")
        dock.setWidget(self.explorador)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        dock.hide()
        self._dock_explorador = dock

        # --- Menú, toolbar y barra de estado ----------------------------------------------
        self._crear_menu()
        self._crear_toolbar()
        self._crear_statusbar()
        self._conectar_senales()

        # Primer escaneo de proyectos (QThread)
        self.ctl.escanear_proyectos()

    # =========================================================================
    # Construcción de la UI
    # =========================================================================
    def _crear_menu(self) -> None:
        barra = self.menuBar()

        menu_archivo = barra.addMenu("&Archivo")
        accion_prefs = QAction("&Preferencias…", self)
        accion_prefs.setShortcut(QKeySequence("Ctrl+,"))
        accion_prefs.triggered.connect(self._abrir_preferencias)
        accion_salir = QAction("&Salir", self)
        accion_salir.setShortcut(QKeySequence.Quit)
        accion_salir.triggered.connect(self.close)
        menu_archivo.addAction(accion_prefs)
        menu_archivo.addSeparator()
        menu_archivo.addAction(accion_salir)

        menu_ver = barra.addMenu("&Ver")
        accion_explorador = QAction("&Explorador de proyectos", self, checkable=True)
        accion_explorador.setShortcut(QKeySequence("Ctrl+Shift+E"))
        accion_explorador.toggled.connect(
            lambda visible: self._dock_explorador.setVisible(visible))
        self._dock_explorador.visibilityChanged.connect(accion_explorador.setChecked)
        accion_tema = QAction("Alternar tema &claro/oscuro", self)
        accion_tema.triggered.connect(self._alternar_tema)
        menu_ver.addAction(accion_explorador)
        menu_ver.addAction(accion_tema)

        menu_proyecto = barra.addMenu("&Proyecto")
        accion_escanear = QAction("&Reescanear proyectos", self)
        accion_escanear.setShortcut(QKeySequence.Refresh)
        accion_escanear.triggered.connect(self.ctl.escanear_proyectos)
        accion_detener = QAction("&Detener operación actual", self)
        accion_detener.setShortcut(QKeySequence("Ctrl+."))
        accion_detener.triggered.connect(self.ctl.detener)
        menu_proyecto.addAction(accion_escanear)
        menu_proyecto.addAction(accion_detener)

        menu_ayuda = barra.addMenu("A&yuda")
        accion_acerca = QAction("&Acerca de Quarto Studio", self)
        accion_acerca.triggered.connect(self._acerca_de)
        menu_ayuda.addAction(accion_acerca)

    def _crear_toolbar(self) -> None:
        toolbar = QToolBar("Principal")
        toolbar.setObjectName("toolbarPrincipal")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        accion_refrescar = QAction(icono_app("refrescar"), "Reescanear proyectos", self)
        accion_refrescar.triggered.connect(self.ctl.escanear_proyectos)
        accion_detener = QAction(icono_app("detener"), "Detener operación", self)
        accion_detener.triggered.connect(self.ctl.detener)
        accion_explorador = QAction(icono_app("carpeta"), "Explorador de proyectos", self)
        accion_explorador.triggered.connect(
            lambda: self._dock_explorador.setVisible(not self._dock_explorador.isVisible()))
        accion_prefs = QAction(icono_app("configuracion"), "Preferencias", self)
        accion_prefs.triggered.connect(self._abrir_preferencias)

        toolbar.addAction(accion_refrescar)
        toolbar.addAction(accion_detener)
        toolbar.addSeparator()
        toolbar.addAction(accion_explorador)
        toolbar.addAction(accion_prefs)

    def _crear_statusbar(self) -> None:
        barra = QStatusBar()
        self.setStatusBar(barra)
        self._etiqueta_estado = QLabel("Listo")
        self._progreso = QProgressBar()
        self._progreso.setFixedWidth(220)
        self._progreso.setVisible(False)
        self._etiqueta_docs = QLabel(str(settings().docs_dir()))
        barra.addWidget(self._etiqueta_estado, stretch=1)
        barra.addPermanentWidget(self._progreso)
        barra.addPermanentWidget(self._etiqueta_docs)

    # =========================================================================
    # Señales
    # =========================================================================
    def _conectar_senales(self) -> None:
        runner = self.ctl.runner
        runner.iniciado.connect(self.consola.al_iniciar)
        runner.linea_salida.connect(self.consola.al_recibir_linea)
        runner.terminado.connect(self.consola.al_terminar)
        runner.estado_ocupado.connect(self._al_cambiar_ocupado)
        runner.progreso.connect(self._al_progresar)
        self.consola.boton_detener.clicked.connect(self.ctl.detener)

        self.ctl.operacion_registrada.connect(self.logs.registrar)
        self.ctl.operacion_registrada.connect(self.pagina_dashboard.registrar_operacion)
        self.ctl.operacion_rechazada.connect(
            lambda msg: QMessageBox.information(self, "Operación en curso", msg))

        self.ctl.blogs_actualizados.connect(self.pagina_dashboard.actualizar_blogs)
        self.ctl.blogs_actualizados.connect(self.pagina_blogs.actualizar_blogs)
        self.ctl.blogs_actualizados.connect(self.pagina_metadata.actualizar_blogs)
        self.ctl.blogs_actualizados.connect(self.pagina_similares.actualizar_blogs)

    def _cambiar_pagina(self, id_seccion: str) -> None:
        indice = self._indice_paginas.get(id_seccion)
        if indice is not None:
            self._paginas.setCurrentIndex(indice)

    def _al_cambiar_ocupado(self, ocupado: bool) -> None:
        self._progreso.setVisible(ocupado)
        if ocupado:
            self._progreso.setRange(0, 0)  # indeterminado hasta conocer el total
            self._etiqueta_estado.setText("Ejecutando operación…")
        else:
            self._etiqueta_estado.setText("Listo")

    def _al_progresar(self, actual: int, total: int, archivo: str) -> None:
        if total > 0:
            self._progreso.setRange(0, total)
            self._progreso.setValue(min(actual, total))
            porcentaje = int(actual * 100 / total)
            self._etiqueta_estado.setText(f"{porcentaje}% — {archivo}" if archivo else f"{porcentaje}%")
        elif archivo:
            self._etiqueta_estado.setText(archivo)

    # =========================================================================
    # Acciones
    # =========================================================================
    def _abrir_preferencias(self) -> None:
        if PreferencesDialog(self).exec():
            self._etiqueta_docs.setText(str(settings().docs_dir()))
            self.explorador.establecer_raiz(settings().docs_dir())
            self.ctl.escanear_proyectos()

    def _alternar_tema(self) -> None:
        nuevo = "claro" if settings().get("general/tema") == "oscuro" else "oscuro"
        aplicar_tema(nuevo)

    def _acerca_de(self) -> None:
        QMessageBox.about(
            self, f"Acerca de {APP_NAME}",
            f"<b>{APP_NAME} {APP_VERSION}</b><br><br>"
            "Frontend de escritorio (PySide6/Qt6) para las herramientas de "
            "<code>scripts_for_quarto</code>: gestión de blogs Quarto, metadatos, "
            "tags, índices y formato YAML.<br><br>"
            "Los scripts existentes actúan como motor: la interfaz los invoca a "
            "través de una capa de servicios desacoplada.",
        )

    def closeEvent(self, evento) -> None:  # noqa: N802 — API Qt
        self.ctl.detener()
        super().closeEvent(evento)
