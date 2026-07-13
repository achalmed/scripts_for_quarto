"""
new_post_dialog.py — Asistente de creación de posts APAQuarto.

Sustituye al asistente de terminal de 07-post-creator.sh (~50 prompts)
por un formulario con pestañas. Devuelve un DatosPost que post_service
convierte en index.qmd.
"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDialog, QDialogButtonBox, QFormLayout, QLineEdit,
    QPlainTextEdit, QTabWidget, QVBoxLayout, QWidget,
)

from app.services.post_service import DatosPost


def _separar(texto: str) -> list[str]:
    return [t.strip() for t in texto.split(",") if t.strip()]


class NewPostDialog(QDialog):
    def __init__(self, blog_nombre: str, carpetas_posts: list[str], parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"Nueva publicación — {blog_nombre}")
        self.setMinimumWidth(620)

        pestanas = QTabWidget()
        pestanas.addTab(self._tab_basico(carpetas_posts), "Básico")
        pestanas.addTab(self._tab_apa(), "APAQuarto")
        pestanas.addTab(self._tab_resumen(), "Abstract")

        botones = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        botones.accepted.connect(self._validar)
        botones.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(pestanas)
        layout.addWidget(botones)

    # ----------------------------------------------------------------- pestañas
    def _tab_basico(self, carpetas: list[str]) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)
        self._carpeta = QComboBox()
        self._carpeta.setEditable(True)
        self._carpeta.addItems(carpetas or ["posts"])
        self._titulo = QLineEdit()
        self._subtitulo = QLineEdit()
        self._titulo_corto = QLineEdit()
        self._titulo_corto.setPlaceholderText("(auto desde el título)")
        self._tags = QLineEdit()
        self._tags.setPlaceholderText("análisis, econometría, tutorial")
        self._categorias = QLineEdit()
        self._categorias.setPlaceholderText("Análisis, Tutorial (máx. 2)")
        self._lang = QComboBox()
        self._lang.addItems(["es", "en", "fr", "de", "pt"])
        form.addRow("Carpeta de posts:", self._carpeta)
        form.addRow("Título *:", self._titulo)
        form.addRow("Subtítulo:", self._subtitulo)
        form.addRow("Título corto:", self._titulo_corto)
        form.addRow("Tags (comas):", self._tags)
        form.addRow("Categorías (comas):", self._categorias)
        form.addRow("Idioma:", self._lang)
        return w

    def _tab_apa(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)
        self._doc_type = QComboBox()
        self._doc_type.addItems(["jou", "man", "doc", "stu"])
        self._journal = QLineEdit()
        self._volume = QLineEdit()
        self._course = QLineEdit()
        self._professor = QLineEdit()
        self._duedate = QLineEdit()
        self._floats = QCheckBox("Figuras/tablas en el texto (floatsintext)")
        self._lineas = QCheckBox("Números de línea (numbered-lines)")
        self._ampersand = QCheckBox("Usar «y» en vez de «&» (no-ampersand-parenthetical)")
        self._mask = QCheckBox("Revisión ciega (mask)")
        self._meta = QCheckBox("Meta-análisis")
        self._docx = QCheckBox("apaquarto-docx (Word)")
        self._docx.setChecked(True)
        self._html = QCheckBox("apaquarto-html (Web)")
        self._html.setChecked(True)
        self._pdf = QCheckBox("apaquarto-pdf (PDF)")
        self._pdf.setChecked(True)
        self._typst = QCheckBox("apaquarto-typst (Typst)")
        self._bib = QLineEdit("references.bib")
        form.addRow("Tipo de documento:", self._doc_type)
        form.addRow("Revista (jou):", self._journal)
        form.addRow("Volumen (jou):", self._volume)
        form.addRow("Curso (stu):", self._course)
        form.addRow("Profesor (stu):", self._professor)
        form.addRow("Fecha de entrega (stu):", self._duedate)
        form.addRow("Bibliografía:", self._bib)
        for chk in (self._floats, self._lineas, self._ampersand, self._mask, self._meta,
                    self._docx, self._html, self._pdf, self._typst):
            form.addRow("", chk)
        return w

    def _tab_resumen(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)
        self._abstract = QPlainTextEdit()
        self._abstract.setPlaceholderText("Resumen (máx. 250 palabras)…")
        self._keywords = QLineEdit()
        self._keywords.setPlaceholderText("economía, política fiscal, crecimiento (3-5)")
        self._impacto = QLineEdit()
        self._word_count = QCheckBox("Mostrar conteo de palabras")
        form.addRow("Abstract:", self._abstract)
        form.addRow("Keywords (comas):", self._keywords)
        form.addRow("Impact statement:", self._impacto)
        form.addRow("", self._word_count)
        return w

    # ---------------------------------------------------------------- resultado
    def _validar(self) -> None:
        if self._titulo.text().strip():
            self.accept()
        else:
            self._titulo.setFocus()
            self._titulo.setPlaceholderText("⚠ El título es obligatorio")

    def datos(self) -> DatosPost:
        return DatosPost(
            carpeta_posts=self._carpeta.currentText().strip() or "posts",
            titulo=self._titulo.text().strip(),
            subtitulo=self._subtitulo.text().strip(),
            titulo_corto=self._titulo_corto.text().strip(),
            tags=_separar(self._tags.text()),
            categorias=_separar(self._categorias.text())[:2],
            bibliography=self._bib.text().strip() or "references.bib",
            floatsintext=self._floats.isChecked(),
            numbered_lines=self._lineas.isChecked(),
            no_ampersand=self._ampersand.isChecked(),
            mask=self._mask.isChecked(),
            meta_analysis=self._meta.isChecked(),
            impact_statement=self._impacto.text().strip(),
            doc_type=self._doc_type.currentText(),
            journal=self._journal.text().strip(),
            volume=self._volume.text().strip(),
            course=self._course.text().strip(),
            professor=self._professor.text().strip(),
            duedate=self._duedate.text().strip(),
            formato_docx=self._docx.isChecked(),
            formato_html=self._html.isChecked(),
            formato_pdf=self._pdf.isChecked(),
            formato_typst=self._typst.isChecked(),
            abstract=self._abstract.toPlainText().strip().replace('"', "'"),
            keywords=_separar(self._keywords.text()),
            word_count=self._word_count.isChecked(),
            lang=self._lang.currentText(),
        )
