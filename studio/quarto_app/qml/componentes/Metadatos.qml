// Metadatos — la entrada actual de la vista Entradas: su fila del Excel frente a su frontmatter, campo a campo (lo que
// difiere, con color), y el frontmatter entero.
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami
import GuiComun

QQC2.ScrollView {
    id: pagina
    readonly property var f: studio.flujo
    contentWidth: availableWidth
    QQC2.ScrollBar.horizontal.policy: QQC2.ScrollBar.AlwaysOff
    ColumnLayout {
        width: pagina.availableWidth - Kirigami.Units.largeSpacing * 2
        x: Kirigami.Units.largeSpacing
        y: Kirigami.Units.largeSpacing
        spacing: Kirigami.Units.largeSpacing
        Kirigami.PlaceholderMessage {
            Layout.fillWidth: true
            visible: !pagina.f.hayElemento || pagina.f.vistaElemento !== "entradas"
            text: "Ninguna entrada"
            explanation: "Elige una entrada en la tabla: su frontmatter y su fila del Excel, campo a campo."
            icon.name: "text-markdown"
        }
        Kirigami.InlineMessage {
            Layout.fillWidth: true
            visible: pagina.f.avisoExcel !== "" && pagina.f.hayElemento
            type: Kirigami.MessageType.Information
            text: pagina.f.avisoExcel
        }
        Kirigami.Heading { visible: pagina.f.hayElemento && pagina.f.vistaElemento === "entradas"; level: 5; text: pagina.f.enExcel ? (pagina.f.nDiferencias > 0 ? pagina.f.nDiferencias + " campo(s) difieren entre el Excel y el .qmd" : "El Excel y el .qmd coinciden") : "Esta entrada no está en el Excel («Plantilla incremental» la añade)" }
        Repeater {
            model: pagina.f.comparacion
            delegate: ColumnLayout {
                required property var modelData
                Layout.fillWidth: true
                spacing: 0
                QQC2.Label { text: modelData.campo; font: Kirigami.Theme.smallFont; color: modelData.difiere ? Kirigami.Theme.neutralTextColor : Kirigami.Theme.disabledTextColor }
                QQC2.Label { Layout.fillWidth: true; text: ".qmd: " + (modelData.archivo || "—"); wrapMode: Text.Wrap }
                QQC2.Label { Layout.fillWidth: true; text: "Excel: " + (modelData.excel || "—"); wrapMode: Text.Wrap; color: modelData.difiere ? Kirigami.Theme.neutralTextColor : Kirigami.Theme.disabledTextColor }
            }
        }
        Kirigami.Separator { Layout.fillWidth: true; visible: pagina.f.frontmatterCampos.length > 0 }
        Kirigami.Heading { visible: pagina.f.frontmatterCampos.length > 0; level: 5; text: "Frontmatter" }
        Repeater {
            model: pagina.f.frontmatterCampos
            delegate: RowLayout {
                required property var modelData
                Layout.fillWidth: true
                QQC2.Label { text: modelData.campo + ":"; font: Kirigami.Theme.smallFont; color: Kirigami.Theme.disabledTextColor; Layout.preferredWidth: Kirigami.Units.gridUnit * 7; elide: Text.ElideRight }
                QQC2.Label { Layout.fillWidth: true; text: modelData.valor; wrapMode: Text.Wrap; textFormat: Text.PlainText }
            }
        }
        Item { Layout.preferredHeight: Kirigami.Units.largeSpacing }
    }
}
