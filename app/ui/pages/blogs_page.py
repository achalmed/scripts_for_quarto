"""
blogs_page.py — Página Blogs: tabla de proyectos + acciones del Blog Manager.
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QGroupBox, QHBoxLayout, QHeaderView, QInputDialog, QMessageBox,
    QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from app.controllers.blogs_controller import BlogsController
from app.dialogs.new_blog_dialog import NewBlogDialog
from app.dialogs.new_post_dialog import NewPostDialog
from app.models.blog import Blog
from app.services.project_scanner import IGNORAR_DIRS
from app.widgets.page_header import PageHeader

_COLUMNAS = ["Blog", "Posts", "Git", "_quarto.yml", "Ruta"]


class BlogsPage(QWidget):
    def __init__(self, controlador: BlogsController, parent=None) -> None:
        super().__init__(parent)
        self._ctl = controlador
        self._blogs: list[Blog] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.addWidget(PageHeader(
            "Blogs",
            "Gestión de los proyectos Quarto (pub_* y website-achalma): "
            "render, preview, publicación, git, backups y creación de contenido.",
        ))

        # --- Tabla de blogs ------------------------------------------------------
        self._tabla = QTableWidget(0, len(_COLUMNAS))
        self._tabla.setHorizontalHeaderLabels(_COLUMNAS)
        self._tabla.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self._tabla.verticalHeader().setVisible(False)
        self._tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self._tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self._tabla.setSelectionMode(QTableWidget.SingleSelection)
        layout.addWidget(self._tabla, stretch=1)

        # --- Acciones sobre el blog seleccionado -----------------------------------
        caja_blog = QGroupBox("Blog seleccionado")
        fila_blog = QHBoxLayout(caja_blog)
        for texto, manejador in [
            ("▶ Render", lambda: self._con_blog(self._ctl.render)),
            ("👁 Preview", lambda: self._con_blog(self._ctl.preview)),
            ("■ Detener preview", self._ctl.detener_preview),
            ("🧹 Limpiar", lambda: self._con_blog(self._ctl.clean)),
            ("🌍 Publicar", self._publicar),
            ("✔ Verificar", lambda: self._con_blog(self._ctl.check)),
            ("📄 Posts", lambda: self._con_blog(self._ctl.listar_posts)),
            ("🐙 Git status", lambda: self._con_blog(self._ctl.git_status)),
            ("🐙 Commit+push", self._commit),
            ("＋ Nueva publicación", self._nuevo_post),
        ]:
            boton = QPushButton(texto)
            boton.clicked.connect(manejador)
            fila_blog.addWidget(boton)
        layout.addWidget(caja_blog)

        # --- Operaciones por lotes ---------------------------------------------------
        caja_lotes = QGroupBox("Operaciones por lotes")
        fila_lotes = QHBoxLayout(caja_lotes)
        for texto, manejador, confirmar in [
            ("▶ Render de todos", self._ctl.render_all, True),
            ("🧹 Limpiar todos", self._ctl.clean_all, True),
            ("🧬 Verificar estructura", self._ctl.check_structure, False),
            ("💾 Backup de todos", self._ctl.backup_todos, True),
            ("🆕 Crear blog…", self._nuevo_blog, False),
        ]:
            boton = QPushButton(texto)
            if confirmar:
                boton.clicked.connect(lambda _=False, t=texto, m=manejador: self._confirmar(t, m))
            else:
                boton.clicked.connect(manejador)
            fila_lotes.addWidget(boton)
        fila_lotes.addStretch(1)
        layout.addWidget(caja_lotes)

        self._ctl.post_creado.connect(
            lambda ruta: QMessageBox.information(self, "Post creado", f"Post creado en:\n{ruta}"))
        self._ctl.error.connect(
            lambda msg: QMessageBox.warning(self, "Error", msg))

    # ------------------------------------------------------------------- estado
    def actualizar_blogs(self, blogs: list[Blog]) -> None:
        self._blogs = blogs
        self._tabla.setRowCount(0)
        for blog in blogs:
            fila = self._tabla.rowCount()
            self._tabla.insertRow(fila)
            valores = [
                blog.nombre,
                str(blog.num_posts),
                "✔" if blog.tiene_git else "—",
                "✔" if blog.tiene_quarto_yml else "—",
                str(blog.ruta),
            ]
            for col, valor in enumerate(valores):
                self._tabla.setItem(fila, col, QTableWidgetItem(valor))

    def _blog_actual(self) -> Blog | None:
        fila = self._tabla.currentRow()
        if fila < 0 or fila >= len(self._blogs):
            QMessageBox.information(self, "Blogs", "Selecciona primero un blog en la tabla.")
            return None
        return self._blogs[fila]

    # ------------------------------------------------------------------ acciones
    def _con_blog(self, accion) -> None:
        blog = self._blog_actual()
        if blog:
            accion(blog.nombre)

    def _confirmar(self, titulo: str, accion) -> None:
        if QMessageBox.question(self, titulo, f"¿Ejecutar «{titulo}» sobre TODOS los blogs?") \
                == QMessageBox.Yes:
            accion()

    def _publicar(self) -> None:
        blog = self._blog_actual()
        if blog and QMessageBox.question(
                self, "Publicar",
                f"¿Publicar {blog.nombre}? Esta operación sube el sitio al destino configurado.") \
                == QMessageBox.Yes:
            self._ctl.publish(blog.nombre)

    def _commit(self) -> None:
        blog = self._blog_actual()
        if not blog:
            return
        mensaje, ok = QInputDialog.getText(self, "Commit + push", "Mensaje del commit:")
        if ok and mensaje.strip():
            self._ctl.git_commit(blog.nombre, mensaje.strip())

    def _nuevo_post(self) -> None:
        blog = self._blog_actual()
        if not blog:
            return
        carpetas = sorted(
            d.name for d in Path(blog.ruta).iterdir()
            if d.is_dir() and d.name not in IGNORAR_DIRS and not d.name.startswith(".")
            and any(p.is_dir() for p in d.iterdir())
        ) or ["posts"]
        dialogo = NewPostDialog(blog.nombre, carpetas, self)
        if dialogo.exec():
            self._ctl.crear_post(blog.ruta, dialogo.datos())

    def _nuevo_blog(self) -> None:
        dialogo = NewBlogDialog(self)
        if dialogo.exec():
            self._ctl.init_blog(dialogo.nombre(), dialogo.titulo())
