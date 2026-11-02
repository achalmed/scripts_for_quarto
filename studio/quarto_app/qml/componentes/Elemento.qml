// Elemento — la fila seleccionada del índice del vault (el enlace y su destino) o de los índices de contenido (el
// fragmento en texto).
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami
import GuiComun

Item {
    id: pagina
    readonly property var f: studio.flujo
    readonly property bool conTexto: f.hayElemento && f.elementoTexto !== ""
    VistaTexto {
        anchors.fill: parent
        visible: pagina.conTexto
        texto: pagina.f.elementoTexto
        markdown: false
        definicion: "Markdown"
        nombreAccesible: "Texto de " + pagina.f.elementoTitulo
    }
    QQC2.ScrollView {
        anchors.fill: parent
        visible: !pagina.conTexto
        contentWidth: availableWidth
        QQC2.ScrollBar.horizontal.policy: QQC2.ScrollBar.AlwaysOff
        ColumnLayout {
            width: parent.availableWidth - Kirigami.Units.largeSpacing * 2
            x: Kirigami.Units.largeSpacing
            y: Kirigami.Units.largeSpacing
            spacing: Kirigami.Units.largeSpacing
            Kirigami.PlaceholderMessage {
                Layout.fillWidth: true
                visible: !pagina.f.hayElemento
                text: "Nada seleccionado"
                explanation: "Elige una fila de la tabla."
                icon.name: "view-list-details"
            }
            Repeater {
                model: pagina.f.elementoCampos
                delegate: ColumnLayout {
                    required property var modelData
                    Layout.fillWidth: true
                    spacing: 0
                    QQC2.Label { text: modelData.etiqueta; font: Kirigami.Theme.smallFont; color: Kirigami.Theme.disabledTextColor }
                    QQC2.Label { Layout.fillWidth: true; text: modelData.valor; wrapMode: Text.WrapAnywhere; textFormat: Text.PlainText }
                }
            }
        }
    }
}
