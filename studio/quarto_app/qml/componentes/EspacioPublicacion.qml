// EspacioPublicacion — el área Publicación (reingeniería E8–E10): a dónde va el sitio y qué lleva. Arriba el proyecto y su
// dominio de destino con las comprobaciones de que el destino corresponde al sitio (dominio del registro, site-url del
// _quarto.yml, remoto origin, rama con su remoto); el estado de construcción por la regla de la puerta R6; los archivos
// que cambiarán; la última publicación y el historial (los commits del remoto que tocaron _site/); la salida de la última
// corrida sobre el sitio. Renderizar
// (el sitio entero, Ctrl+Mayús+B), simular y publicar: publicar confirma con la base nombrando el sitio y el dominio, y no se ofrece si el
// destino no corresponde. Solo lee: lo que escribe es la CLI del gestor de blogs.
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami
import GuiComun

QQC2.ScrollView {
    id: raiz
    readonly property var s: studio.sitios
    readonly property var p: studio.publicacion
    function accion(n) { return studio.acciones.accion(n) }
    // los niveles con iconos simbólicos en su color semántico (no los emblemas a color, que en Oscuro pintan
    // «información» con el acento rojo)
    // (signos de texto, no iconos: Kirigami.Icon no recolorea los simbólicos de Colloid)
    function signoNivel(n) { return n === "positivo" ? "✓" : (n === "negativo" ? "✕" : (n === "neutro" ? "!" : "·")) }
    function colorNivel(n) {
        return n === "positivo" ? Kirigami.Theme.positiveTextColor : n === "negativo" ? Kirigami.Theme.negativeTextColor
             : n === "neutro" ? Kirigami.Theme.neutralTextColor : Kirigami.Theme.activeTextColor
    }

    contentWidth: availableWidth
    QQC2.ScrollBar.horizontal.policy: QQC2.ScrollBar.AlwaysOff

    ColumnLayout {
        width: raiz.availableWidth - Kirigami.Units.largeSpacing * 4
        x: Kirigami.Units.largeSpacing * 2
        spacing: Kirigami.Units.largeSpacing

        Kirigami.PlaceholderMessage {
            Layout.fillWidth: true
            Layout.topMargin: Kirigami.Units.gridUnit * 4
            visible: !raiz.s.hayActual
            icon.name: "cloud-upload-symbolic"
            text: "Elige un proyecto"
            explanation: "A la izquierda: el hub y los pubs con su estado de construcción"
        }

        // el destino: el sitio, a dónde va y, debajo, las tres acciones en fila (la de publicar, la principal)
        ColumnLayout {
            Layout.fillWidth: true
            Layout.topMargin: Kirigami.Units.largeSpacing
            visible: raiz.s.hayActual
            spacing: 0
            Kirigami.Heading { level: 1; text: raiz.s.nombre; Layout.fillWidth: true; elide: Text.ElideRight }
            RowLayout {
                spacing: Kirigami.Units.smallSpacing
                Kirigami.Icon { source: "go-next-symbolic"; implicitWidth: Kirigami.Units.iconSizes.small; implicitHeight: implicitWidth; isMask: true; color: Kirigami.Theme.disabledTextColor }
                Kirigami.Heading {
                    level: 3
                    text: raiz.p.dominio || "sin dominio de destino"
                    color: raiz.p.coincide ? Kirigami.Theme.textColor : Kirigami.Theme.negativeTextColor
                }
                QQC2.ToolButton { icon.name: "internet-web-browser-symbolic"; text: "Abrir el sitio publicado"; display: QQC2.AbstractButton.IconOnly; enabled: raiz.accion("archivo.navegador").habilitada; onClicked: raiz.accion("archivo.navegador").disparar(); Accessible.name: text; QQC2.ToolTip.text: text; QQC2.ToolTip.visible: hovered }
            }
            QQC2.Label { text: raiz.s.tema ? "Tema: " + raiz.s.tema + " · rama " + (raiz.s.rama || "—") : "rama " + (raiz.s.rama || "—"); color: Kirigami.Theme.disabledTextColor }
            Flow {
                Layout.fillWidth: true
                Layout.topMargin: Kirigami.Units.largeSpacing
                spacing: Kirigami.Units.smallSpacing
                BotonAccion { accion: raiz.accion("sitio.renderizar"); plano: false; horizontalPadding: Kirigami.Units.largeSpacing }
                BotonAccion { accion: raiz.accion("sitio.simular_publicar"); plano: false; horizontalPadding: Kirigami.Units.largeSpacing }
                BotonPrincipal {
                    accion: raiz.accion("sitio.publicar")
                    text: "Publicar en " + (raiz.p.dominio || "…")
                    icon.name: "cloud-upload-symbolic"
                    QQC2.ToolTip.text: enabled ? "Confirma nombrando el sitio y el dominio; Netlify despliega con el push" : (raiz.p.coincide ? "No disponible ahora: simula primero la publicación (F5), o hay una operación en curso" : raiz.p.motivo)
                    QQC2.ToolTip.visible: hovered
                }
            }
        }
        Kirigami.InlineMessage {
            Layout.fillWidth: true
            visible: raiz.s.hayActual && raiz.p.hayDestino && !raiz.p.coincide
            type: Kirigami.MessageType.Error
            text: "<b>El destino no corresponde a «" + raiz.s.nombre + "».</b> " + raiz.p.motivo + ". No se ofrece publicar hasta que coincida."
        }

        GridLayout {
            Layout.fillWidth: true
            visible: raiz.s.hayActual
            columns: raiz.width > Kirigami.Units.gridUnit * 50 ? 2 : 1
            columnSpacing: Kirigami.Units.gridUnit
            rowSpacing: Kirigami.Units.largeSpacing

            // comprobaciones del destino
            ColumnLayout {
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignTop
                Kirigami.Heading { level: 3; text: "¿El destino es el de este sitio?" }
                Repeater {
                    model: raiz.p.comprobaciones
                    delegate: RowLayout {
                        required property var modelData
                        Layout.fillWidth: true
                        QQC2.Label { text: raiz.signoNivel(modelData.nivel); color: raiz.colorNivel(modelData.nivel); font.weight: Font.Bold; Layout.alignment: Qt.AlignTop; Layout.preferredWidth: Kirigami.Units.iconSizes.small; horizontalAlignment: Text.AlignHCenter; Accessible.ignored: true }
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 0
                            QQC2.Label { text: modelData.nombre; font.weight: Font.DemiBold }
                            QQC2.Label { text: modelData.detalle; wrapMode: Text.WordWrap; Layout.fillWidth: true; color: modelData.ok === false ? Kirigami.Theme.negativeTextColor : Kirigami.Theme.disabledTextColor }
                        }
                    }
                }
            }
            // estado de construcción y última publicación
            ColumnLayout {
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignTop
                Kirigami.Heading { level: 3; text: "Estado de construcción" }
                RowLayout {
                    EtiquetaNivel {
                        text: raiz.s.estadoTexto
                        nivel: raiz.s.estadoClave === "al_dia" ? "positivo" : (raiz.s.estadoClave === "problemas" ? "negativo" : (raiz.s.estadoClave === "sin_render" ? "neutro" : "activo"))
                    }
                }
                QQC2.Label { text: raiz.s.motivo; wrapMode: Text.WordWrap; Layout.fillWidth: true; color: Kirigami.Theme.disabledTextColor }
                Kirigami.FormLayout {
                    Layout.fillWidth: true
                    wideMode: true
                    QQC2.Label { Kirigami.FormData.label: "Último render confirmado:"; text: raiz.s.fechaRender }
                    QQC2.Label { Kirigami.FormData.label: "Últimas fuentes confirmadas:"; text: raiz.s.fechaFuentes }
                    QQC2.Label {
                        Kirigami.FormData.label: "Última publicación:"
                        text: raiz.p.ultima.fecha ? raiz.p.ultima.fecha + " · " + raiz.p.ultima.commit + " · " + raiz.p.ultima.mensaje : "ninguna en el remoto"
                        wrapMode: Text.WordWrap
                        maximumLineCount: 2
                        elide: Text.ElideRight
                        Layout.fillWidth: true
                    }
                }
            }
        }

        // los archivos que cambiarán
        Kirigami.Heading { level: 3; visible: raiz.s.hayActual; text: "Lo que se publicará · " + raiz.p.totalArchivos }
        QQC2.Label { visible: raiz.s.hayActual; text: raiz.p.resumenArchivos; color: Kirigami.Theme.disabledTextColor; wrapMode: Text.WordWrap; Layout.fillWidth: true }
        TablaDatos {
            Layout.fillWidth: true
            // la altura de lo que lleva (hasta seis filas), no un hueco fijo
            Layout.preferredHeight: Kirigami.Units.gridUnit * (2.4 + 1.7 * Math.min(Math.max(raiz.p.totalArchivos, 1), 6))
            visible: raiz.s.hayActual && raiz.p.totalArchivos > 0
            modelo: raiz.p.archivosModelo
            claveAjustes: "publicacion-archivos"
            umbralEstrecho: 0
            mensajeVacio: "Nada por publicar"
            iconoVacio: "checkmark-symbolic"
            columnas: [{ ancho: 0, minimo: 16, mono: true }, { ancho: 4, semantica: true }, { ancho: 9, secundaria: true }]
        }

        // las entradas que la publicación lleva, con su veredicto de «Antes de publicar» (C15.1)
        Kirigami.Heading { level: 3; visible: raiz.s.hayActual && studio.entrega.entradas.length > 0; text: "Antes de publicar · " + studio.entrega.resumenEntradas }
        Repeater {
            model: raiz.s.hayActual ? studio.entrega.entradas : []
            delegate: RowLayout {
                required property var modelData
                Layout.fillWidth: true
                QQC2.Label { text: raiz.signoNivel(modelData.nivel); color: raiz.colorNivel(modelData.nivel); font.weight: Font.Bold; Layout.preferredWidth: Kirigami.Units.iconSizes.small; horizontalAlignment: Text.AlignHCenter; Accessible.ignored: true }
                QQC2.Label { text: modelData.titulo; font.weight: Font.DemiBold; elide: Text.ElideRight; Layout.maximumWidth: raiz.width * 0.45 }
                QQC2.Label { text: modelData.veredicto + " · " + modelData.revisado; color: Kirigami.Theme.disabledTextColor; elide: Text.ElideRight; Layout.fillWidth: true }
                QQC2.Button {
                    text: "Revisar"
                    icon.name: "checkmark"
                    onClicked: { ventana.abrirDocumento(modelData.ruta); Qt.callLater(() => studio.interfaz.abrir("antes_de_publicar")) }
                    QQC2.ToolTip.text: "Abre la entrada y su «Antes de publicar» (Ctrl+Alt+E)"
                    QQC2.ToolTip.visible: hovered
                }
            }
        }

        // el historial
        Kirigami.Heading { level: 3; visible: raiz.s.hayActual; text: "Historial de publicaciones" }
        TablaDatos {
            Layout.fillWidth: true
            Layout.preferredHeight: Kirigami.Units.gridUnit * 10
            visible: raiz.s.hayActual
            modelo: raiz.p.historialModelo
            claveAjustes: "publicacion-historial"
            umbralEstrecho: 0
            mensajeVacio: "El remoto no tiene ningún commit que haya tocado _site/"
            iconoVacio: "view-history-symbolic"
            columnas: [{ ancho: 6, mono: true }, { ancho: 10, secundaria: true }, { ancho: 0, minimo: 14 }, { ancho: 5, alinear: "derecha", secundaria: true }]
        }
        Kirigami.Heading { level: 3; visible: raiz.s.hayActual; text: "La última corrida sobre el sitio" }
        Registro {
            Layout.fillWidth: true
            Layout.preferredHeight: Kirigami.Units.gridUnit * 10
            visible: raiz.s.hayActual
        }
        Item { Layout.preferredHeight: Kirigami.Units.largeSpacing }
    }
}
