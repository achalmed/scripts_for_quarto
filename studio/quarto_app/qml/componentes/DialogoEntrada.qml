// DialogoEntrada — «Nueva entrada…» (Ctrl+N): los campos del asistente de terminal de posts APAQuarto (Básico, APAQuarto,
// Resumen) en un formulario; `sitios.crearEntrada` genera el mismo index.qmd (post_service) en el sitio actual.
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami
import org.kde.kirigamiaddons.formcard as FormCard
import GuiComun

Kirigami.Dialog {
    id: dialogo
    readonly property var s: studio.sitios
    title: "Nueva entrada" + (s.hayActual ? " en " + s.nombre : "")
    preferredWidth: Kirigami.Units.gridUnit * 36
    preferredHeight: Kirigami.Units.gridUnit * 30
    standardButtons: Kirigami.Dialog.Cancel
    customFooterActions: [Kirigami.Action {
        text: "Crear"; icon.name: "document-new"; enabled: titulo.text.trim() !== ""
        onTriggered: {
            const error = dialogo.s.crearEntrada({
                carpeta_posts: carpeta.editText || carpeta.currentText || "posts", titulo: titulo.text, subtitulo: subtitulo.text, titulo_corto: tituloCorto.text,
                tags: tags.text, categorias: categorias.text, lang: lang.currentText, bibliography: bib.text || "references.bib",
                doc_type: tipo.currentText, journal: journal.text, volume: volume.text, course: course.text, professor: professor.text, duedate: duedate.text,
                floatsintext: floats.checked, numbered_lines: lineas.checked, no_ampersand: ampersand.checked, mask: mask.checked, meta_analysis: meta.checked,
                formato_docx: docx.checked, formato_html: html.checked, formato_pdf: pdf.checked, formato_typst: typst.checked,
                abstract: abstracto.text, keywords: keywords.text, impact_statement: impacto.text, word_count: wordCount.checked })
            if (error) ventana.mensajes.mostrar(error, "error")
            else { ventana.mensajes.mostrar("Entrada creada en " + dialogo.s.entradaNombre + ": ábrela con Intro en la pestaña Entradas.", "positivo"); dialogo.close() }
        }
    }]
    function abrir() {
        if (!s.hayActual) { ventana.mensajes.mostrar("Elige primero un sitio.", "aviso"); return }
        carpeta.model = s.carpetasDeEntradas()
        titulo.text = ""; subtitulo.text = ""; tituloCorto.text = ""; tags.text = ""; categorias.text = ""; abstracto.text = ""; keywords.text = ""; impacto.text = ""
        open()
        titulo.forceActiveFocus()
    }
    QQC2.ScrollView {
        contentWidth: availableWidth
        ColumnLayout {
            width: parent.availableWidth
            spacing: 0
            FormCard.FormHeader { title: "Básico" }
            FormCard.FormCard {
                FormCard.FormComboBoxDelegate { id: carpeta; text: "Carpeta de entradas"; editable: true; model: ["posts"] }
                FormCard.FormTextFieldDelegate { id: titulo; label: "Título (obligatorio)" }
                FormCard.FormTextFieldDelegate { id: subtitulo; label: "Subtítulo" }
                FormCard.FormTextFieldDelegate { id: tituloCorto; label: "Título corto"; placeholderText: "(desde el título)" }
                FormCard.FormTextFieldDelegate { id: tags; label: "Tags (comas)"; placeholderText: "análisis, econometría" }
                FormCard.FormTextFieldDelegate { id: categorias; label: "Categorías (comas, máximo 2)" }
                FormCard.FormComboBoxDelegate { id: lang; text: "Idioma"; model: ["es", "en", "fr", "de", "pt"]; currentIndex: 0 }
            }
            FormCard.FormHeader { title: "APAQuarto" }
            FormCard.FormCard {
                FormCard.FormComboBoxDelegate { id: tipo; text: "Tipo de documento"; model: ["jou", "man", "doc", "stu"]; currentIndex: 0 }
                FormCard.FormTextFieldDelegate { id: journal; label: "Revista (jou)" }
                FormCard.FormTextFieldDelegate { id: volume; label: "Volumen (jou)" }
                FormCard.FormTextFieldDelegate { id: course; label: "Curso (stu)" }
                FormCard.FormTextFieldDelegate { id: professor; label: "Profesor (stu)" }
                FormCard.FormTextFieldDelegate { id: duedate; label: "Fecha de entrega (stu)" }
                FormCard.FormTextFieldDelegate { id: bib; label: "Bibliografía"; text: "references.bib" }
                FormCard.FormCheckDelegate { id: floats; text: "Figuras y tablas en el texto (floatsintext)" }
                FormCard.FormCheckDelegate { id: lineas; text: "Números de línea (numbered-lines)" }
                FormCard.FormCheckDelegate { id: ampersand; text: "«y» en vez de «&» (no-ampersand-parenthetical)" }
                FormCard.FormCheckDelegate { id: mask; text: "Revisión ciega (mask)" }
                FormCard.FormCheckDelegate { id: meta; text: "Meta-análisis" }
                FormCard.FormCheckDelegate { id: docx; text: "apaquarto-docx (Word)"; checked: true }
                FormCard.FormCheckDelegate { id: html; text: "apaquarto-html (web)"; checked: true }
                FormCard.FormCheckDelegate { id: pdf; text: "apaquarto-pdf (PDF)"; checked: true }
                FormCard.FormCheckDelegate { id: typst; text: "apaquarto-typst (Typst)" }
            }
            FormCard.FormHeader { title: "Resumen" }
            FormCard.FormCard {
                FormCard.FormTextFieldDelegate { id: abstracto; label: "Abstract (máximo 250 palabras)" }
                FormCard.FormTextFieldDelegate { id: keywords; label: "Keywords (comas, 3 a 5)" }
                FormCard.FormTextFieldDelegate { id: impacto; label: "Impact statement" }
                FormCard.FormCheckDelegate { id: wordCount; text: "Mostrar el conteo de palabras" }
            }
        }
    }
}
