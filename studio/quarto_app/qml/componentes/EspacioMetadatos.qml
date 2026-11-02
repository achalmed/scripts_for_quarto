// EspacioMetadatos — el área Metadatos (reingeniería E7): el Excel frente a los .qmd de TODAS las entradas del sitio
// (las que difieren, las que no tienen fila en el Excel, las filas del Excel sin documento) y, de la elegida, la
// comparación campo a campo. Nada se sobrescribe aquí: «Ver diferencias» corre el gestor de metadatos sin escribir y
// «Llevar el Excel a los documentos…» es la operación que simula primero y aplica tras confirmar.
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami
import GuiComun

ColumnLayout {
    id: raiz
    readonly property var m: studio.metadatos
    readonly property var ops: studio.operaciones
    function tabla() { return lista }
    spacing: 0

    RowLayout {
        Layout.fillWidth: true
        Layout.margins: Kirigami.Units.smallSpacing
        spacing: Kirigami.Units.largeSpacing
        Kirigami.Icon { source: "view-list-details"; implicitWidth: Kirigami.Units.iconSizes.medium; implicitHeight: implicitWidth }
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 0
            Kirigami.Heading { level: 3; text: "El Excel frente a los documentos" + (studio.sitios.hayActual ? " · " + studio.sitios.nombre : "") }
            QQC2.Label { text: raiz.m.resumen || (studio.flujo.avisoExcel || "Elige un proyecto"); color: Kirigami.Theme.disabledTextColor; wrapMode: Text.WordWrap; Layout.fillWidth: true }
        }
        QQC2.Button {
            text: "Ver diferencias (gestor)"
            icon.name: "system-run"
            enabled: studio.sitios.hayActual && !studio.tareas.activa
            onClicked: { raiz.ops.fijar("diferencias"); raiz.ops.simular() }
            QQC2.ToolTip.text: "El gestor de metadatos compara el Excel con los documentos sin escribir nada (la salida, en Herramientas › Salida)"
            QQC2.ToolTip.visible: hovered
        }
        QQC2.Button {
            text: "Llevar el Excel a los documentos…"
            icon.name: "document-import"
            enabled: studio.sitios.hayActual && !studio.tareas.activa
            onClicked: { raiz.ops.fijar("aplicar_excel"); studio.interfaz.pedir("aplicar", {}) }
            QQC2.ToolTip.text: "Aplica las celdas del Excel donde difieren (una celda vacía borra el campo): primero se ve la orden y lo que toca"
            QQC2.ToolTip.visible: hovered
        }
        BotonAccion { accion: studio.acciones.accion("archivo.excel"); conTexto: false }
    }
    Kirigami.InlineMessage {
        Layout.fillWidth: true
        visible: raiz.m.soloExcel.length > 0
        type: Kirigami.MessageType.Information
        text: raiz.m.soloExcel.length + " fila(s) del Excel no tienen documento: " + raiz.m.soloExcel.slice(0, 4).join(", ") + (raiz.m.soloExcel.length > 4 ? "…" : "")
    }
    QQC2.SplitView {
        Layout.fillWidth: true
        Layout.fillHeight: true
        TablaDatos {
            id: lista
            QQC2.SplitView.fillWidth: true
            QQC2.SplitView.minimumWidth: Kirigami.Units.gridUnit * 20
            modelo: raiz.m.modelo
            claveAjustes: "diagnostico"
            umbralEstrecho: Kirigami.Units.gridUnit * 34
            mensajeVacio: studio.sitios.hayActual ? "Este sitio no tiene entradas (carpetas AAAA-MM-DD-título con index.qmd)" : "Elige un proyecto"
            iconoVacio: "text-markdown"
            columnas: [{ ancho: 7, mono: true }, { ancho: 0, minimo: 14, conIcono: true }, { ancho: 12, semantica: true }, { ancho: 18, secundaria: true, estrecho: true }]
            onFilaActualCambiada: fila => raiz.m.fijarFila(fila)
            onActivada: fila => { raiz.m.fijarFila(fila); studio.interfaz.pedir("editar", { ruta: raiz.m.rutaActual }) }
        }
        ColumnLayout {
            QQC2.SplitView.preferredWidth: Kirigami.Units.gridUnit * 28
            QQC2.SplitView.minimumWidth: Kirigami.Units.gridUnit * 16
            spacing: 0
            RowLayout {
                Layout.fillWidth: true
                Layout.margins: Kirigami.Units.smallSpacing
                Kirigami.Heading { level: 4; text: raiz.m.hayActual ? raiz.m.tituloActual : "Campo a campo"; Layout.fillWidth: true; elide: Text.ElideRight }
                QQC2.ToolButton {
                    visible: raiz.m.hayActual
                    icon.name: "document-edit"
                    text: "Editar"
                    onClicked: studio.interfaz.pedir("editar", { ruta: raiz.m.rutaActual })
                }
            }
            TablaDatos {
                Layout.fillWidth: true
                Layout.fillHeight: true
                modelo: raiz.m.camposModelo
                claveAjustes: "diagnostico-campos"
                umbralEstrecho: 0
                mensajeVacio: raiz.m.hayActual ? "Esta entrada no tiene fila en el Excel" : "Elige una entrada: sus campos en el documento y en el Excel"
                iconoVacio: "view-list-details"
                columnas: [{ ancho: 8, mono: true, semantica: true }, { ancho: 0, minimo: 10 }, { ancho: 0, minimo: 10 }]
            }
        }
    }
}
