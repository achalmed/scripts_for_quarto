// BarraRender — la franja de abajo (la forma de escritor aprobada el 2026-11-18): a la izquierda, el estado del render
// (en curso, el último de la sesión con su resultado, o el último confirmado del sitio) y sus problemas; a la derecha,
// los sitios con cambios sin publicar (sin render o con render sin publicar), cada uno lleva a su vista de publicación.
// Sin datos propios: studio.operaciones (ultimoRender, renderEnCurso), studio.sitios (pendientes, nProblemas), studio.tareas.
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami

QQC2.ToolBar {
    id: raiz
    readonly property var o: studio.operaciones
    readonly property var s: studio.sitios
    readonly property var r: o.ultimoRender
    readonly property bool hayRender: r.id !== undefined
    readonly property bool fallo: hayRender && r.codigo !== 0
    signal irAPublicacion(string sitio)
    signal verProblemas()

    position: QQC2.ToolBar.Footer
    Accessible.name: "Estado del render y sitios sin publicar"

    function textoRender() {
        if (o.renderEnCurso) return "Renderizando: " + (studio.tareas.elemento || studio.tareas.nombre)
        if (hayRender) {
            const que = r.objeto + (r.sitio && r.objeto !== r.sitio ? " (" + r.sitio + ")" : "")
            return (fallo ? "El render de " + que + " falló (código " + r.codigo + ")" : "Renderizado " + que)
                   + " · " + r.hora + " · " + r.segundos.toLocaleString(Qt.locale(), "f", 1) + " s"
        }
        if (s.hayActual) return "Sin render en esta sesión · último render confirmado de " + s.nombre + ": " + s.fechaRender
        return "Sin render en esta sesión"
    }

    RowLayout {
        anchors.fill: parent
        spacing: Kirigami.Units.smallSpacing

        // el estado del render
        Kirigami.Icon {
            implicitWidth: Kirigami.Units.iconSizes.small; implicitHeight: implicitWidth
            source: raiz.o.renderEnCurso ? "run-build" : (raiz.fallo ? "data-error" : (raiz.hayRender ? "data-success" : "run-build"))
            Accessible.name: raiz.fallo ? "El render falló" : "Estado del render"
        }
        QQC2.Label {
            Layout.fillWidth: true
            Layout.minimumWidth: Kirigami.Units.gridUnit * 8
            text: raiz.textoRender()
            elide: Text.ElideRight
            color: raiz.fallo ? Kirigami.Theme.negativeTextColor : (raiz.hayRender || raiz.o.renderEnCurso ? Kirigami.Theme.textColor : Kirigami.Theme.disabledTextColor)
            QQC2.ToolTip.text: text
            QQC2.ToolTip.visible: zonaRender.hovered && truncated
            HoverHandler { id: zonaRender }
        }
        QQC2.ToolButton {
            visible: raiz.s.hayActual && raiz.s.nProblemas > 0
            text: raiz.s.resumenProblemas
            icon.name: "data-warning"
            onClicked: raiz.verProblemas()
            QQC2.ToolTip.text: "Los errores y avisos del último render de " + raiz.s.nombre + ", con su archivo y su línea"
            QQC2.ToolTip.visible: hovered
        }

        Kirigami.Separator { Layout.fillHeight: true; Layout.margins: Kirigami.Units.smallSpacing }

        // los sitios con cambios sin publicar
        QQC2.Label {
            text: raiz.s.pendientes.length ? "Sin publicar:" : "Todos los sitios publicados"
            color: Kirigami.Theme.disabledTextColor
        }
        Repeater {
            model: raiz.s.pendientes
            delegate: QQC2.ToolButton {
                required property var modelData
                text: modelData.nombre
                icon.name: modelData.clave === "sin_render" ? "data-warning" : "data-information"
                checkable: false
                highlighted: modelData.nombre === raiz.s.nombre
                onClicked: raiz.irAPublicacion(modelData.nombre)
                Accessible.name: modelData.nombre + ", " + modelData.estado
                QQC2.ToolTip.text: modelData.estado + ": " + modelData.motivo
                QQC2.ToolTip.visible: hovered
                QQC2.ToolTip.delay: Kirigami.Units.toolTipDelay
            }
        }
    }
}
