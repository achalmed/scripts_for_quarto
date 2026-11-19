// DialogoAntesDePublicar — «Antes de publicar…» (Ctrl+Alt+E; campo 15 de la norma del flujo de conocimiento): los controles
// del motor de escritura sobre la entrada abierta, por grupo, con su estado, su porqué con la fuente y sus hallazgos (un
// clic lleva al archivo y la línea); los puntos manuales con su casilla y su nota; el veredicto «Listo para publicar» o
// «Faltan N»; «Revisar de nuevo» (mide la corrida), «Traer las cifras…» (simula y luego escribe _cifras.yml) y «Dar por
// revisado…» (la constancia; con faltas pide el motivo). Ningún control se calcula aquí: todo es studio.entrega.
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami
import GuiComun

Kirigami.Dialog {
    id: dialogo
    readonly property var e: studio.entrega
    title: "Antes de publicar" + (e.titulo ? " · " + e.titulo : "")
    preferredWidth: Kirigami.Units.gridUnit * 44
    preferredHeight: Kirigami.Units.gridUnit * 36
    standardButtons: Kirigami.Dialog.Close
    customFooterActions: [
        Kirigami.Action { text: "Revisar de nuevo"; icon.name: "view-refresh"; enabled: !dialogo.e.revisando; onTriggered: dialogo.e.revisarMidiendo() },
        Kirigami.Action { text: "Traer las cifras…"; icon.name: "office-chart-line"; enabled: !dialogo.e.revisando; onTriggered: dialogo.e.cifras(false) },
        Kirigami.Action { text: "Dar por revisado…"; icon.name: "checkmark"; enabled: !dialogo.e.revisando && dialogo.e.veredicto !== ""
                          onTriggered: { if (dialogo.e.listo) dialogo.e.darPorRevisado(""); else { motivo.text = ""; dialogoMotivo.open() } } }
    ]

    function abrir() {
        if (!e.disponible) { ventana.mensajes.mostrar(e.motivo, "pista"); return }
        e.revisar()
        open()
    }

    Connections {
        target: dialogo.e
        function onCifrasListas(d) {
            if (d.error) { ventana.mensajes.mostrar(d.error, "error"); return }
            if (d.escrito) { ventana.mensajes.mostrar("_cifras.yml al día con " + d.paquetes.join(", ") + ".", "positivo"); return }
            dialogoCifras.dato = d
            dialogoCifras.open()
        }
        function onConstanciaLista(d) {
            if (d.error) ventana.mensajes.mostrar(d.error, "error")
            else if (d.bloqueado) { motivo.text = ""; dialogoMotivo.open() }
            else if (d.escrito) ventana.mensajes.mostrar("Revisado para publicar: " + d.constancia.veredicto + " (en " + d.archivo + ").", "positivo")
        }
        function onFalsoDeclarado(d) { if (d.error) ventana.mensajes.mostrar(d.error, "error") }
        function onMarcado(d) { if (d.error) ventana.mensajes.mostrar(d.error, "error") }
    }

    ColumnLayout {
        spacing: Kirigami.Units.smallSpacing
        RowLayout {
            Layout.fillWidth: true
            Layout.margins: Kirigami.Units.smallSpacing
            EtiquetaNivel {
                visible: dialogo.e.veredicto !== ""
                text: dialogo.e.veredicto
                nivel: dialogo.e.listo ? "positivo" : "negativo"
            }
            QQC2.Label {
                Layout.fillWidth: true
                text: dialogo.e.revisando ? "Revisando…" : dialogo.e.resumenTexto
                color: Kirigami.Theme.disabledTextColor
                elide: Text.ElideRight
            }
            QQC2.Label {
                visible: !!dialogo.e.revisado.fecha
                text: dialogo.e.revisado.fecha ? "Revisado el " + String(dialogo.e.revisado.fecha).replace("T", " ").slice(0, 16)
                                                 + (dialogo.e.revisado.vigente ? "" : ", cambió después") : ""
                color: Kirigami.Theme.disabledTextColor
            }
        }
        Kirigami.InlineMessage {
            Layout.fillWidth: true
            visible: dialogo.e.error !== ""
            type: Kirigami.MessageType.Error
            text: dialogo.e.error
        }
        QQC2.ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.preferredHeight: Kirigami.Units.gridUnit * 28
            ListView {
                id: lista
                model: dialogo.e.filas
                clip: true
                spacing: Kirigami.Units.smallSpacing
                delegate: Loader {
                    required property var modelData
                    width: lista.width
                    sourceComponent: modelData.tipo === "grupo" ? grupo : fila
                    property var dato: modelData
                }
            }
        }
    }

    Component {
        id: grupo
        Kirigami.ListSectionHeader { text: dato.nombre; width: lista.width }
    }
    Component {
        id: fila
        RowLayout {
            width: lista.width
            spacing: Kirigami.Units.largeSpacing
            Kirigami.Icon { source: dato.icono; implicitWidth: Kirigami.Units.iconSizes.smallMedium; implicitHeight: implicitWidth; Layout.alignment: Qt.AlignTop }
            ColumnLayout {
                Layout.fillWidth: true
                spacing: 0
                RowLayout {
                    Layout.fillWidth: true
                    QQC2.CheckBox {
                        visible: dato.manual
                        checked: dato.marcado === "hecho"
                        onToggled: dialogo.e.marcar(dato.id, checked, nota.text)
                        Accessible.name: dato.nombre
                    }
                    QQC2.Label { text: dato.nombre; font.weight: Font.DemiBold; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                    QQC2.ToolButton {
                        visible: dato.estado === "aviso" || dato.estado === "falla"
                        text: "Falso positivo…"
                        icon.name: "dialog-cancel"
                        display: QQC2.AbstractButton.IconOnly
                        onClicked: { dialogoFalso.control = dato.id; dialogoFalso.nombre = dato.nombre; notaFalso.text = ""; dialogoFalso.open() }
                        QQC2.ToolTip.text: text; QQC2.ToolTip.visible: hovered
                        Accessible.name: text
                    }
                }
                QQC2.Label { visible: dato.detalle !== ""; text: dato.detalle; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                QQC2.TextField {
                    id: nota
                    visible: dato.manual
                    Layout.fillWidth: true
                    text: dato.nota
                    placeholderText: "Nota, o por qué no aplica (sin casilla, queda justificado)"
                    onEditingFinished: if (text !== dato.nota) dialogo.e.marcar(dato.id, dato.marcado === "hecho", text)
                }
                Repeater {
                    model: dato.hallazgos
                    delegate: QQC2.Label {
                        required property var modelData
                        Layout.fillWidth: true
                        text: "<a href='#'>" + modelData.archivo + (modelData.linea > 0 ? ":" + modelData.linea : "") + "</a> " + modelData.texto
                        textFormat: Text.StyledText
                        wrapMode: Text.WordWrap
                        onLinkActivated: ventana.abrirEnLinea(modelData.ruta, modelData.linea)
                        HoverHandler { cursorShape: Qt.PointingHandCursor }
                    }
                }
                QQC2.Label {
                    text: "Por qué: " + dato.porque + (dato.fuente ? " · " + dato.fuente : "") + (dato.medido ? " · " + dato.medido : "")
                    color: Kirigami.Theme.disabledTextColor
                    wrapMode: Text.WordWrap
                    Layout.fillWidth: true
                }
            }
        }
    }

    Kirigami.PromptDialog {
        id: dialogoCifras
        property var dato: ({})
        title: "Traer las cifras de " + (dato.paquetes ? dato.paquetes.join(", ") : "")
        subtitle: dato.paquetes ? ("Se escribirá " + dato.archivo + ": " + (dato.cambian || []).length + " cambian, " + (dato.nuevas || []).length + " nuevas, "
                                   + (dato.quitadas || []).length + " se quitan y " + dato.iguales + " quedan iguales."
                                   + ((dato.cambian || []).length ? "\n\nCambian: " + dato.cambian.slice(0, 8).map(c => c.clave + " " + c.antes + " → " + c.despues).join("; ") : "")
                                   + ((dato.choques || []).length ? "\n\nNo se puede escribir: la misma clave en dos paquetes (" + dato.choques.join("; ") + ")." : "")
                                   + (dato.carga_el_archivo ? "" : "\n\nEl post aún no carga el archivo: añada «metadata-files: [_cifras.yml]» a su frontmatter.")
                                   + "\n\nEn el texto, cada número se escribe {{< meta cifras.<clave> >}}.") : ""
        standardButtons: Kirigami.Dialog.Cancel
        customFooterActions: [Kirigami.Action { text: "Escribir _cifras.yml"; icon.name: "document-save"; enabled: !(dialogoCifras.dato.choques || []).length
                                                onTriggered: { dialogo.e.cifras(true); dialogoCifras.close() } }]
    }
    Kirigami.PromptDialog {
        id: dialogoMotivo
        title: "Faltan " + dialogo.e.faltan + ": ¿publicar igual?"
        subtitle: "La constancia queda en _registro/publicacion.yml con lo que faltaba y este motivo."
        standardButtons: Kirigami.Dialog.Cancel
        QQC2.TextField { id: motivo; placeholderText: "Por qué se publica con lo que falta" }
        customFooterActions: [Kirigami.Action { text: "Dar por revisado de todos modos"; icon.name: "checkmark"; enabled: motivo.text.trim() !== ""
                                                onTriggered: { dialogo.e.darPorRevisado(motivo.text); dialogoMotivo.close() } }]
    }
    Kirigami.PromptDialog {
        id: dialogoFalso
        property string control: ""
        property string nombre: ""
        title: "Falso positivo: " + nombre
        subtitle: "Lo que marcó este control no era un defecto. La nota queda en _registro/controles.yml para medir el control (C14.1)."
        standardButtons: Kirigami.Dialog.Cancel
        QQC2.TextField { id: notaFalso; placeholderText: "No era error porque…" }
        customFooterActions: [Kirigami.Action { text: "Declarar"; icon.name: "dialog-ok-apply"; enabled: notaFalso.text.trim() !== ""
                                                onTriggered: { dialogo.e.falso(dialogoFalso.control, notaFalso.text); dialogoFalso.close() } }]
    }
}
