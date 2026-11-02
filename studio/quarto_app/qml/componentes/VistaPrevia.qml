// VistaPrevia — la página renderizada del documento abierto (reingeniería E5): el HTML de `_site/` en QtWebEngine del
// sistema, con atrás, adelante, recargar y la lista de páginas del sitio para navegar; desde una página se puede editar
// su documento. Sin `_site` o sin QtWebEngine, el documento en Markdown (VistaTexto). Se recarga sola tras un render.
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami
import GuiComun

ColumnLayout {
    id: raiz
    readonly property var d: studio.documentos
    readonly property bool web: d.hayWebEngine && d.urlPagina !== ""
    property string urlActual: d.urlPagina
    signal editar(string ruta)
    spacing: 0

    QQC2.ToolBar {
        Layout.fillWidth: true
        RowLayout {
            anchors.fill: parent
            spacing: Kirigami.Units.smallSpacing
            QQC2.ToolButton { icon.name: "go-previous"; text: "Atrás"; display: QQC2.AbstractButton.IconOnly; enabled: raiz.web && cargador.item && cargador.item.canGoBack; onClicked: cargador.item.goBack(); Accessible.name: text }
            QQC2.ToolButton { icon.name: "go-next"; text: "Adelante"; display: QQC2.AbstractButton.IconOnly; enabled: raiz.web && cargador.item && cargador.item.canGoForward; onClicked: cargador.item.goForward(); Accessible.name: text }
            QQC2.ToolButton { icon.name: "view-refresh"; text: "Recargar"; display: QQC2.AbstractButton.IconOnly; enabled: raiz.web; onClicked: cargador.item.reload(); Accessible.name: text }
            QQC2.ComboBox {
                id: paginas
                Layout.fillWidth: true
                visible: raiz.web
                model: raiz.d.paginas
                textRole: "rel"
                currentIndex: raiz.d.paginas.findIndex(p => p.url === raiz.urlActual)
                displayText: currentIndex >= 0 ? currentText : (raiz.urlActual.split("/_site/").pop() || "Páginas del sitio")
                onActivated: i => { if (cargador.item) cargador.item.url = raiz.d.paginas[i].url }
                Accessible.name: "Páginas del sitio"
            }
            QQC2.Label {
                Layout.fillWidth: true
                visible: !raiz.web
                text: raiz.d.hayWebEngine ? "Sin render: el documento en Markdown" : "Sin QtWebEngine: el documento en Markdown"
                color: Kirigami.Theme.disabledTextColor
                elide: Text.ElideRight
            }
            QQC2.ToolButton {
                id: editarPagina
                property string fuente: ""
                visible: raiz.web && fuente !== "" && fuente !== raiz.d.actual
                icon.name: "document-edit"
                text: "Editar esta página"
                onClicked: raiz.editar(fuente)
            }
        }
    }
    Item {
        Layout.fillWidth: true
        Layout.fillHeight: true
        Loader {
            id: cargador
            anchors.fill: parent
            active: raiz.web && raiz.visible
            source: "VistaWeb.qml"
            onLoaded: {
                item.destino = Qt.binding(() => raiz.d.urlPagina)
                item.version = Qt.binding(() => raiz.d.version)
                item.navegada.connect(u => { raiz.urlActual = u; editarPagina.fuente = raiz.d.documentoDePagina(u) })
            }
        }
        VistaTexto {
            anchors.fill: parent
            visible: !raiz.web
            texto: raiz.d.textoDocumento
            markdown: true
            mensajeVacio: raiz.d.actual === "" ? "Abre un documento: su página renderizada aparece aquí" : "Este documento no tiene vista previa"
            iconoVacio: "view-preview"
            nombreAccesible: "Vista previa"
        }
    }
    QQC2.Label {
        Layout.fillWidth: true
        Layout.margins: Kirigami.Units.smallSpacing
        visible: raiz.web && !raiz.d.paginaDelDocumento && raiz.d.actual !== ""
        text: "Este documento todavía no tiene página en _site: se muestra la portada (Ctrl+Mayús+K renderiza)."
        wrapMode: Text.WordWrap
        font: Kirigami.Theme.smallFont
        color: Kirigami.Theme.neutralTextColor
    }
}
