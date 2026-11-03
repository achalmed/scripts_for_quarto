// EspacioEscritura — el área Escribir (reingeniería E4–E5; el de LaTeX Studio adaptado): las pestañas de los documentos
// abiertos con el editor y la barra de búsqueda; a la derecha la vista previa del sitio (F7 la oculta). Cada documento
// abierto tiene su EditorTexto de gui-comun (su texto y su deshacer); el aviso de «cambió fuera» y la confirmación de sobrescribir
// viven aquí. Sin datos propios: studio.editor (abiertos), studio.documentos, studio.sitios.
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami
import GuiComun

QQC2.SplitView {
    id: raiz

    property bool mostrarPrevia: true
    readonly property var editorActual: editores.count > 0 && studio.editor.indiceActual >= 0 ? editores.itemAt(studio.editor.indiceActual) : null

    orientation: Qt.Horizontal

    function editorDe(ruta) {
        for (let i = 0; i < editores.count; i++) { const e = editores.itemAt(i); if (e && e.ruta === ruta) return e }
        return null
    }
    function abrir(ruta, linea) {
        const i = studio.editor.abrir(ruta)
        if (i < 0) return
        Qt.callLater(() => { const e = editorDe(ruta); if (e && linea > 0) e.irALinea(linea, 0); else if (e) e.area.forceActiveFocus() })
    }
    function guardar(e, forzar) {
        if (!e) return
        const r = e.guardar(forzar)
        if (r === "externo") { confirmarSobrescribir.editor = e; confirmarSobrescribir.open() }
        else if (r !== "") ventana.mensajes.mostrar(r, "error")
    }
    function guardarTodo() {
        for (let i = 0; i < editores.count; i++) { const e = editores.itemAt(i); if (e && e.modificado) guardar(e, false) }
    }
    function cerrarActual() {
        const e = editorActual
        if (!e) return
        if (e.modificado) { confirmarCerrar.editor = e; confirmarCerrar.open() }
        else studio.editor.cerrar(e.ruta)
    }

    Connections {
        target: studio.editor
        function onCambioExterno(ruta) {
            const e = raiz.editorDe(ruta)
            if (!e) return
            if (!e.modificado) { e.recargarDesdeDisco(); ventana.mensajes.mostrar(ruta.split("/").pop() + " cambió fuera de la ventana: recargado.", "informacion") }
            else { cambioFuera.ruta = ruta; cambioFuera.visible = true }
        }
    }

    ColumnLayout {
        QQC2.SplitView.fillWidth: true
        QQC2.SplitView.minimumWidth: Kirigami.Units.gridUnit * 20
        spacing: 0

        // la barra de pestañas solo existe con archivos abiertos (el estilo de KDE falla con una TabBar vacía)
        Loader {
            Layout.fillWidth: true
            active: studio.editor.abiertos.filas > 0
            visible: active
            sourceComponent: Component {
                QQC2.TabBar {
                    currentIndex: studio.editor.indiceActual
                    Accessible.name: "Archivos abiertos"
                    Repeater {
                        model: studio.editor.abiertos
                        delegate: QQC2.TabButton {
                            required property var model
                            required property int index
                            width: implicitWidth
                            // una entrada es siempre index.qmd: la pestaña lleva el nombre de su carpeta
                            text: (model.modificado ? "● " : "") + (model.nombre === "index.qmd" && model.carpeta ? model.carpeta.split("/").pop() : model.nombre)
                            icon.name: model.solo_lectura ? "object-locked" : ""
                            onClicked: studio.editor.fijarActual(model.ruta)
                            QQC2.ToolTip.text: model.ruta
                            QQC2.ToolTip.visible: hovered
                            QQC2.ToolTip.delay: Kirigami.Units.toolTipDelay
                            TapHandler { acceptedButtons: Qt.MiddleButton; onTapped: { studio.editor.fijarActual(model.ruta); raiz.cerrarActual() } }
                        }
                    }
                }
            }
        }

        Kirigami.InlineMessage {
            id: cambioFuera
            property string ruta: ""
            Layout.fillWidth: true
            type: Kirigami.MessageType.Warning
            text: ruta.split("/").pop() + " cambió en el disco y aquí tiene cambios sin guardar."
            visible: false
            actions: [
                Kirigami.Action { text: "Recargar del disco"; icon.name: "view-refresh"; onTriggered: { const e = raiz.editorDe(cambioFuera.ruta); if (e) e.recargarDesdeDisco(); cambioFuera.visible = false } },
                Kirigami.Action { text: "Mantener lo mío"; icon.name: "dialog-ok"; onTriggered: cambioFuera.visible = false }
            ]
        }

        StackLayout {
            id: pila
            Layout.fillWidth: true
            Layout.fillHeight: true
            currentIndex: studio.editor.indiceActual
            Repeater {
                id: editores
                model: studio.editor.abiertos
                delegate: EditorTexto {
                    required property var model
                    controlador: studio.editor
                    ajustarLineas: true                 // la prosa de un .qmd se lee mejor partida
                    ruta: model.ruta
                    definicion: model.definicion
                    soloLectura: model.solo_lectura
                    Component.onCompleted: cargar()
                }
            }
        }

        Kirigami.PlaceholderMessage {
            Layout.fillWidth: true
            Layout.fillHeight: true
            visible: studio.editor.abiertos.filas === 0
            icon.name: "document-edit"
            text: studio.sitios.hayActual ? "Elige un documento del sitio" : "Elige un proyecto"
            explanation: studio.sitios.hayActual ? "Los documentos de «" + studio.sitios.nombre + "» están a la izquierda (Ctrl+P busca uno); la vista previa muestra su página renderizada."
                                                 : "El hub y los pubs están a la izquierda, con su estado de construcción."
        }

        BarraBuscarReemplazar {
            id: busqueda
            Layout.fillWidth: true
            editor: raiz.editorActual
        }

        QQC2.ToolBar {
            Layout.fillWidth: true
            position: QQC2.ToolBar.Footer
            visible: raiz.editorActual !== null
            RowLayout {
                anchors.fill: parent
                spacing: Kirigami.Units.largeSpacing
                QQC2.Label {
                    text: raiz.editorActual ? "Línea " + raiz.editorActual.lineaActual + ", columna " + (raiz.editorActual.columnaActual + 1) : ""
                    font: Kirigami.Theme.smallFont
                }
                QQC2.Label {
                    Layout.fillWidth: true
                    text: raiz.editorActual ? raiz.editorActual.ruta : ""
                    elide: Text.ElideMiddle
                    font: Kirigami.Theme.smallFont
                    color: Kirigami.Theme.disabledTextColor
                }
                QQC2.Label {
                    text: raiz.editorActual ? (raiz.editorActual.definicion || "texto") + (raiz.editorActual.soloLectura ? " · solo lectura" : "") : ""
                    font: Kirigami.Theme.smallFont
                    color: Kirigami.Theme.disabledTextColor
                }
            }
        }
    }

    VistaPrevia {
        id: previa
        visible: raiz.mostrarPrevia
        QQC2.SplitView.preferredWidth: Kirigami.Units.gridUnit * 30
        QQC2.SplitView.minimumWidth: Kirigami.Units.gridUnit * 14
        onEditar: ruta => raiz.abrir(ruta, 0)
    }

    function buscar(reemplazar) { busqueda.abrir(reemplazar) }

    Kirigami.PromptDialog {
        id: confirmarSobrescribir
        property var editor: null
        title: "El archivo cambió en el disco"
        subtitle: (editor ? editor.ruta.split("/").pop() : "") + " se modificó fuera de la ventana desde que lo abriste. Si guardas, lo que hay en el disco se pierde."
        standardButtons: Kirigami.Dialog.Cancel
        customFooterActions: [
            Kirigami.Action { text: "Recargar del disco"; icon.name: "view-refresh"; onTriggered: { confirmarSobrescribir.editor.recargarDesdeDisco(); confirmarSobrescribir.close() } },
            Kirigami.Action { text: "Sobrescribir"; icon.name: "document-save"; onTriggered: { raiz.guardar(confirmarSobrescribir.editor, true); confirmarSobrescribir.close() } }
        ]
    }
    Kirigami.PromptDialog {
        id: confirmarCerrar
        property var editor: null
        title: "Cambios sin guardar"
        subtitle: (editor ? editor.ruta.split("/").pop() : "") + " tiene cambios sin guardar. ¿Guardarlos antes de cerrar?"
        standardButtons: Kirigami.Dialog.Cancel
        customFooterActions: [
            Kirigami.Action { text: "Descartar"; icon.name: "edit-delete"; onTriggered: { studio.editor.cerrar(confirmarCerrar.editor.ruta); confirmarCerrar.close() } },
            Kirigami.Action { text: "Guardar y cerrar"; icon.name: "document-save"; onTriggered: { const e = confirmarCerrar.editor; if (e.guardar(false) === "") studio.editor.cerrar(e.ruta); confirmarCerrar.close() } }
        ]
    }
}
