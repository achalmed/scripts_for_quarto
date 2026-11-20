// PanelProyectos — el árbol de sitios y entradas de la izquierda (la forma de escritor aprobada el 2026-11-18; antes, dos
// listas): los sitios (el hub y los pubs del registro, con su estado de construcción por la regla de la puerta R6 y su
// dominio) y, desplegados bajo el sitio actual, sus documentos por carpeta, cada entrada en una fila con su título y su
// fecha. Un clic en un sitio lo elige; en un documento, lo abre en el editor. Fuera de Escribir quedan solo los sitios.
// Las filas las arma studio.arbol (Python); aquí solo se pintan.
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami
import GuiComun

ColumnLayout {
    id: raiz
    readonly property var s: studio.sitios
    readonly property var d: studio.documentos
    readonly property var a: studio.arbol
    property bool conDocumentos: true
    signal abrirDocumento(string ruta)
    function enfocarDocumentos() { filtro.forceActiveFocus(); filtro.selectAll() }
    // el estado de construcción de un sitio: un punto en su color semántico (no los emblemas a color de Colloid, que en
    // Oscuro pintan «información» con el acento rojo; y Kirigami.Icon no recolorea los simbólicos de Colloid)
    function colorEstado(clave) {
        return clave === "al_dia" ? Kirigami.Theme.positiveTextColor : clave === "problemas" ? Kirigami.Theme.negativeTextColor
             : clave === "sin_render" ? Kirigami.Theme.neutralTextColor : Kirigami.Theme.activeTextColor
    }
    // el documento abierto es del sitio actual: entonces la elegida es su fila y el sitio solo lleva la marca
    readonly property bool hayDocumento: conDocumentos && d.actual !== "" && s.ruta !== "" && d.actual.indexOf(s.ruta) === 0

    spacing: 0
    Kirigami.Theme.colorSet: Kirigami.Theme.View
    Kirigami.Theme.inherit: false

    Kirigami.ListSectionHeader {
        Layout.fillWidth: true
        text: raiz.conDocumentos ? "Sitios y entradas" : "Sitios · " + raiz.s.total
    }
    Kirigami.SearchField {
        id: filtro
        Layout.fillWidth: true
        Layout.margins: Kirigami.Units.smallSpacing
        visible: raiz.conDocumentos
        placeholderText: "Ruta o título (Ctrl+P)"
        onTextChanged: raiz.a.filtrar(text)
        Keys.onDownPressed: arbol.forceActiveFocus()
        Keys.onReturnPressed: { const r = raiz.a.primeraRuta(); if (r) raiz.abrirDocumento(r) }
        Accessible.name: "Buscar un documento del sitio"
    }
    QQC2.ScrollView {
        Layout.fillWidth: true
        Layout.fillHeight: true
        ListView {
            id: arbol
            clip: true
            model: raiz.a.modelo
            keyNavigationEnabled: true
            Accessible.name: "Sitios y entradas"
            delegate: QQC2.ItemDelegate {
                id: fila
                required property var model
                required property int index
                readonly property bool esSitio: model.tipo === "sitio"
                readonly property bool esCarpeta: model.tipo === "carpeta"
                readonly property bool esDocumento: model.tipo === "documento"
                readonly property bool aLaVista: esSitio || raiz.conDocumentos
                width: ListView.view.width
                height: aLaVista ? implicitHeight : 0
                visible: aLaVista
                leftPadding: Kirigami.Units.smallSpacing + model.nivel * Kirigami.Units.gridUnit
                readonly property bool esActual: esSitio && model.sitio === raiz.s.nombre
                // una sola fila elegida: el documento abierto o, sin él, el sitio actual
                highlighted: esSitio ? esActual && !raiz.hayDocumento : (esDocumento && model.ruta === raiz.d.actual)
                hoverEnabled: true
                // el acabado de la familia: la elegida teñida del acento con su marca a la izquierda, nunca el bloque
                // lleno de highlightColor; el sitio del documento abierto conserva solo la marca
                background: FondoSeleccion {
                    elegida: fila.highlighted
                    sobre: fila.hovered
                    pulsada: fila.pressed
                    foco: fila.visualFocus
                    redondeada: false
                    // el sitio del documento abierto: solo la marca, tenue
                    Rectangle {
                        visible: fila.esActual && !fila.highlighted
                        anchors.left: parent.left
                        anchors.verticalCenter: parent.verticalCenter
                        width: Kirigami.Units.smallSpacing * 0.75
                        height: parent.height - Kirigami.Units.smallSpacing * 2
                        color: Kirigami.Theme.highlightColor
                        opacity: 0.6
                    }
                }
                function activar() {
                    if (esSitio) raiz.a.elegirSitio(model.sitio)
                    else if (esCarpeta) raiz.a.alternar(model.clave)
                    else raiz.abrirDocumento(model.ruta)
                }
                onClicked: { arbol.currentIndex = index; activar() }
                Keys.onReturnPressed: activar()
                Keys.onRightPressed: if (model.plegable && !model.abierta) raiz.a.alternar(model.clave)
                Keys.onLeftPressed: if (model.plegable && model.abierta) raiz.a.alternar(model.clave)
                Accessible.name: model.texto + (esSitio ? ", " + model.estadoTexto : "") + (model.detalle ? ", " + model.detalle : "")
                QQC2.ToolTip.text: model.motivo
                QQC2.ToolTip.visible: hovered && model.motivo !== ""
                QQC2.ToolTip.delay: Kirigami.Units.toolTipDelay

                contentItem: RowLayout {
                    spacing: Kirigami.Units.smallSpacing
                    // la flecha de lo que se despliega; los documentos dejan su hueco para alinearse
                    Kirigami.Icon {
                        visible: raiz.conDocumentos      // fuera de Escribir no se despliega nada: sin flechas
                        implicitWidth: Kirigami.Units.iconSizes.small; implicitHeight: implicitWidth
                        source: fila.model.plegable ? (fila.model.abierta ? "go-down-symbolic" : "go-next-symbolic") : ""
                        color: Kirigami.Theme.disabledTextColor
                        isMask: true
                        TapHandler { enabled: fila.model.plegable; onTapped: raiz.a.alternar(fila.model.clave) }
                        Accessible.name: fila.model.plegable ? (fila.model.abierta ? "Plegar " : "Desplegar ") + fila.model.texto : ""
                    }
                    Kirigami.Icon {
                        // los documentos ya llevan su título y su fecha: sin el icono diminuto de tipo de archivo
                        visible: !fila.esDocumento
                        source: fila.model.icono
                        implicitWidth: fila.esSitio ? Kirigami.Units.iconSizes.smallMedium : Kirigami.Units.iconSizes.small
                        implicitHeight: implicitWidth
                        isMask: true
                        color: fila.esCarpeta ? Kirigami.Theme.disabledTextColor : Kirigami.Theme.textColor
                    }
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 0
                        QQC2.Label {
                            Layout.fillWidth: true
                            text: fila.model.texto
                            font.weight: fila.esSitio || fila.highlighted ? Font.DemiBold : Font.Normal
                            elide: Text.ElideRight
                            color: fila.esCarpeta ? Kirigami.Theme.disabledTextColor : Kirigami.Theme.textColor
                        }
                        QQC2.Label {
                            Layout.fillWidth: true
                            visible: fila.model.detalle !== "" && !fila.esCarpeta
                            text: fila.model.detalle
                            font: Kirigami.Theme.smallFont
                            elide: Text.ElideRight
                            color: Kirigami.Theme.disabledTextColor
                        }
                    }
                    QQC2.Label {                     // cuántos documentos hay en la carpeta
                        visible: fila.esCarpeta
                        text: fila.model.detalle
                        font: Kirigami.Theme.smallFont
                        color: Kirigami.Theme.disabledTextColor
                    }
                    QQC2.Label {                     // el estado de construcción del sitio (R6): un punto de su color
                        visible: fila.esSitio
                        text: "●"
                        color: raiz.colorEstado(fila.model.estado)
                        Accessible.name: fila.model.estadoTexto
                        QQC2.ToolTip.text: fila.model.estadoTexto
                        QQC2.ToolTip.visible: zonaEstado.hovered
                        HoverHandler { id: zonaEstado }
                    }
                }
            }
            Kirigami.PlaceholderMessage {
                anchors.centerIn: parent
                width: parent.width - Kirigami.Units.gridUnit * 2
                visible: arbol.count === 0
                text: "Ningún sitio en el registro"
            }
        }
    }
}
