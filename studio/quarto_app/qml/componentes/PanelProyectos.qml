// PanelProyectos — el explorador de la izquierda (reingeniería E2–E3): los proyectos (el hub y los pubs del registro,
// con su estado de construcción por la regla de la puerta R6 y su dominio) y, debajo, los documentos del proyecto
// elegido por carpetas (las entradas con su título y su fecha), filtrables. Un clic abre el documento en el editor.
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami

QQC2.SplitView {
    id: raiz
    readonly property var s: studio.sitios
    readonly property var d: studio.documentos
    property bool conDocumentos: true
    signal abrirDocumento(string ruta)
    function enfocarDocumentos() { filtroDocs.forceActiveFocus(); filtroDocs.selectAll() }

    orientation: Qt.Vertical
    Kirigami.Theme.colorSet: Kirigami.Theme.View
    Kirigami.Theme.inherit: false

    function icono(clave) { return clave === "al_dia" ? "data-success" : (clave === "problemas" ? "data-error" : (clave === "sin_render" ? "data-warning" : "data-information")) }

    // los proyectos
    ColumnLayout {
        QQC2.SplitView.preferredHeight: raiz.conDocumentos ? raiz.height * 0.42 : raiz.height
        QQC2.SplitView.minimumHeight: Kirigami.Units.gridUnit * 6
        spacing: 0
        Rectangle { Layout.fillWidth: true; Layout.fillHeight: true; color: Kirigami.Theme.backgroundColor
            ColumnLayout {
                anchors.fill: parent
                spacing: 0
                Kirigami.ListSectionHeader { Layout.fillWidth: true; text: "Proyectos · " + raiz.s.total }
                QQC2.ScrollView {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    ListView {
                        id: proyectos
                        clip: true
                        model: raiz.s.proyectos
                        delegate: QQC2.ItemDelegate {
                            id: fila
                            required property var modelData
                            width: ListView.view.width
                            highlighted: modelData.nombre === raiz.s.nombre
                            onClicked: raiz.s.fijarPorNombre(modelData.nombre)
                            Accessible.name: modelData.nombre + ", " + modelData.estado
                            QQC2.ToolTip.text: modelData.motivo
                            QQC2.ToolTip.visible: hovered
                            QQC2.ToolTip.delay: Kirigami.Units.toolTipDelay
                            contentItem: RowLayout {
                                spacing: Kirigami.Units.smallSpacing
                                Kirigami.Icon { source: fila.modelData.esHub ? "go-home" : "folder-html"; implicitWidth: Kirigami.Units.iconSizes.smallMedium; implicitHeight: implicitWidth }
                                ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: 0
                                    QQC2.Label {
                                        Layout.fillWidth: true
                                        text: fila.modelData.nombre + (fila.modelData.esHub ? " (hub)" : "")
                                        font.weight: Font.DemiBold
                                        elide: Text.ElideRight
                                        color: fila.highlighted ? Kirigami.Theme.highlightedTextColor : Kirigami.Theme.textColor
                                    }
                                    QQC2.Label {
                                        Layout.fillWidth: true
                                        text: (fila.modelData.dominio || "sin dominio") + " · " + fila.modelData.entradas + " entradas"
                                        font: Kirigami.Theme.smallFont
                                        elide: Text.ElideRight
                                        color: fila.highlighted ? Kirigami.Theme.highlightedTextColor : Kirigami.Theme.disabledTextColor
                                    }
                                }
                                Kirigami.Icon {
                                    source: raiz.icono(fila.modelData.clave)
                                    implicitWidth: Kirigami.Units.iconSizes.small; implicitHeight: implicitWidth
                                    Accessible.name: fila.modelData.estado
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    // los documentos del proyecto
    ColumnLayout {
        visible: raiz.conDocumentos
        QQC2.SplitView.fillHeight: true
        QQC2.SplitView.minimumHeight: Kirigami.Units.gridUnit * 6
        spacing: 0
        Rectangle { Layout.fillWidth: true; Layout.fillHeight: true; color: Kirigami.Theme.backgroundColor
            ColumnLayout {
                anchors.fill: parent
                spacing: 0
                Kirigami.ListSectionHeader { Layout.fillWidth: true; text: "Documentos" + (raiz.s.hayActual ? " de " + raiz.s.nombre + " · " + raiz.d.total : "") }
                Kirigami.SearchField {
                    id: filtroDocs
                    Layout.fillWidth: true
                    Layout.margins: Kirigami.Units.smallSpacing
                    placeholderText: "Ruta o título (Ctrl+P)"
                    onTextChanged: raiz.d.filtrar(text)
                    Keys.onDownPressed: documentos.forceActiveFocus()
                    Keys.onReturnPressed: { const r = raiz.d.rutaDe(0); if (r) raiz.abrirDocumento(r) }
                    Accessible.name: "Buscar un documento"
                }
                QQC2.ScrollView {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    ListView {
                        id: documentos
                        clip: true
                        model: raiz.d.modelo
                        keyNavigationEnabled: true
                        section.property: "carpeta"
                        section.delegate: Kirigami.ListSectionHeader { required property string section; width: ListView.view.width; text: section; font: Kirigami.Theme.smallFont }
                        delegate: QQC2.ItemDelegate {
                            id: doc
                            required property var model
                            required property int index
                            width: ListView.view.width
                            highlighted: model.ruta === raiz.d.actual
                            onClicked: raiz.abrirDocumento(model.ruta)
                            Keys.onReturnPressed: raiz.abrirDocumento(model.ruta)
                            Accessible.name: model.rel
                            contentItem: RowLayout {
                                spacing: Kirigami.Units.smallSpacing
                                Kirigami.Icon { source: doc.model.icono; implicitWidth: Kirigami.Units.iconSizes.small; implicitHeight: implicitWidth }
                                ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: 0
                                    QQC2.Label {
                                        Layout.fillWidth: true
                                        text: doc.model.titulo || doc.model.nombre
                                        elide: Text.ElideRight
                                        color: doc.highlighted ? Kirigami.Theme.highlightedTextColor : Kirigami.Theme.textColor
                                    }
                                    QQC2.Label {
                                        Layout.fillWidth: true
                                        visible: doc.model.titulo !== "" || doc.model.fecha !== ""
                                        text: (doc.model.fecha ? doc.model.fecha + " · " : "") + doc.model.nombre
                                        font: Kirigami.Theme.smallFont
                                        elide: Text.ElideRight
                                        color: doc.highlighted ? Kirigami.Theme.highlightedTextColor : Kirigami.Theme.disabledTextColor
                                    }
                                }
                            }
                        }
                        Kirigami.PlaceholderMessage {
                            anchors.centerIn: parent
                            width: parent.width - Kirigami.Units.gridUnit * 2
                            visible: documentos.count === 0
                            text: raiz.s.hayActual ? "Ningún documento" : "Elige un proyecto"
                        }
                    }
                }
            }
        }
    }
}
