// Main.qml — Quarto Studio (reingeniería del 2026-11-02, docs/reingenieria.md): un entorno de escritura y publicación de
// la familia de sitios Quarto sobre GuiComun.VentanaBase, al modo de RStudio y VS Code con Quarto. Arriba, las cuatro
// áreas (Escribir · Metadatos · Publicación · Herramientas, Ctrl+1–4), el proyecto con su estado de construcción,
// Renderizar (Ctrl+Mayús+K) y Publicar. A la izquierda, los proyectos y los documentos del proyecto. En el centro, el
// área: el editor con la vista previa; el diagnóstico de metadatos; la vista de publicación; las tablas y operaciones
// de siempre. Ninguna llamada al disco ni a un backend aquí: todo lo hacen los controladores de Python (studio.*).
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami
import GuiComun
import "componentes"

VentanaBase {
    id: ventana

    readonly property var espacio: studio.espacio
    readonly property var registro: studio.acciones
    readonly property var sitios: studio.sitios
    readonly property var flujo: studio.flujo
    readonly property var ops: studio.operaciones
    readonly property string area: espacio.area

    title: (area === "escribir" && studio.editor.actual ? studio.editor.actual.split("/").pop() + " · " : "")
           + (sitios.hayActual ? sitios.nombre : "Quarto") + " — Quarto Studio"
    acciones: registro
    tareas: studio.tareas
    consola: studio.consola
    descripcion: descripcionStudio
    autor: "Edison Achalma (@achalmed)"
    claveAjustes: "ventana-3"
    width: 1440
    height: 900

    function accion(nombre) { return registro.accion(nombre) }
    function espacioActual() { return [escritura, metadatos, publicacion, herramientas][espacio.indiceArea] }
    function abrirDocumento(ruta) { if (!ruta) return; espacio.fijarArea("escribir"); escritura.abrir(ruta, 0) }

    Connections {
        target: studio.interfaz
        function onPedir(nombre, datos) {
            switch (nombre) {
            case "filtrar":
                if (ventana.area === "escribir" && escritura.editorActual) escritura.buscar(false)
                else { const t = espacioActual().tabla ? espacioActual().tabla() : null; if (t) t.forceActiveFocus() }
                break
            case "guardar": escritura.guardar(escritura.editorActual, false); break
            case "ir_documento": espacio.fijarArea("escribir"); proyectos.enfocarDocumentos(); break
            case "previa": escritura.mostrarPrevia = !escritura.mostrarPrevia; break
            case "editar": abrirDocumento(datos.ruta); break
            case "seleccionar_todo": { const e = espacioActual(); const t = e.tabla ? e.tabla() : null; if (t && t.seleccionarTodo) t.seleccionarTodo(); break }
            case "aplicar": dialogoAplicar.abrir(); break
            case "nueva_entrada": dialogoEntrada.abrir(); break
            case "venv": dialogoVenv.open(); break
            case "pestana": espacio.fijarArea("herramientas"); herramientas.pestana = datos.indice; break
            case "paleta": ventana.paleta.abrir(datos.texto || ""); break
            }
        }
    }
    Connections { target: espacio; function onAviso(texto, tipo) { ventana.mensajes.mostrar(texto, tipo) } }
    Connections { target: sitios; function onAviso(texto, tipo) { ventana.mensajes.mostrar(texto, tipo) } }
    Connections { target: flujo; function onAviso(texto, tipo) { ventana.mensajes.mostrar(texto, tipo) } }
    Connections { target: studio.editor; function onAviso(texto, tipo) { ventana.mensajes.mostrar(texto, tipo) } }
    Connections {
        target: ops
        function onAviso(texto, tipo) { ventana.mensajes.mostrar(texto, tipo) }
        function onTerminada(id, aplicar, codigo) {
            if (aplicar && (id === "render" || id === "render_entrada") && sitios.nProblemas > 0) { espacio.fijarArea("herramientas"); herramientas.pestana = 2 }
            else if (ventana.area === "herramientas") herramientas.pestana = 4
        }
    }

    // ------------------------------------------------------------------ la cabecera
    header: QQC2.ToolBar {
        position: QQC2.ToolBar.Header
        contentItem: RowLayout {
            spacing: Kirigami.Units.smallSpacing
            QQC2.TabBar {
                currentIndex: espacio.indiceArea
                onCurrentIndexChanged: espacio.fijarAreaPorIndice(currentIndex)
                Repeater {
                    model: 4                       // fijas: el TabBar del estilo de KDE no admite crearse vacío
                    delegate: QQC2.TabButton {
                        required property int index
                        readonly property var a: espacio.areas[index]
                        text: a.texto
                        icon.name: a.icono
                        width: implicitWidth
                        QQC2.ToolTip.text: "Ctrl+" + (index + 1)
                        QQC2.ToolTip.visible: hovered
                    }
                }
            }
            Item { Layout.fillWidth: true }
            // el proyecto y su estado de construcción
            QQC2.Control {
                id: chip
                visible: sitios.hayActual
                padding: Kirigami.Units.smallSpacing
                leftPadding: Kirigami.Units.largeSpacing
                rightPadding: Kirigami.Units.largeSpacing
                background: Rectangle {
                    radius: height / 2
                    color: sitios.estadoClave === "al_dia" ? Kirigami.Theme.positiveBackgroundColor
                           : (sitios.estadoClave === "problemas" ? Kirigami.Theme.negativeBackgroundColor : Kirigami.Theme.neutralBackgroundColor)
                }
                contentItem: RowLayout {
                    spacing: Kirigami.Units.smallSpacing
                    Kirigami.Icon { source: sitios.esHub ? "go-home" : "folder-html"; implicitWidth: Kirigami.Units.iconSizes.small; implicitHeight: implicitWidth }
                    QQC2.Label { text: sitios.nombre + " · " + sitios.estadoTexto; font.weight: Font.DemiBold }
                }
                QQC2.ToolTip.text: sitios.motivo
                QQC2.ToolTip.visible: zonaChip.hovered
                HoverHandler { id: zonaChip }
                Accessible.name: "Proyecto " + sitios.nombre + ": " + sitios.estadoTexto
            }
            BotonAccion { accion: ventana.accion("sitio.renderizar") }
            QQC2.ToolButton {
                text: "Publicar"
                icon.name: "cloud-upload"
                enabled: sitios.hayActual
                onClicked: espacio.fijarArea("publicacion")
                QQC2.ToolTip.text: "La vista de publicación: a dónde va el sitio y qué lleva"
                QQC2.ToolTip.visible: hovered
            }
            BotonAccion { accion: ventana.accion("ventana.paleta"); conTexto: false }
        }
    }

    // ------------------------------------------------------------------ proyectos · área
    RowLayout {
        anchors.fill: parent
        spacing: 0
        PanelProyectos {
            id: proyectos
            Layout.preferredWidth: Kirigami.Units.gridUnit * 17
            Layout.fillHeight: true
            conDocumentos: ventana.area === "escribir"
            onAbrirDocumento: ruta => ventana.abrirDocumento(ruta)
        }
        Kirigami.Separator { Layout.fillHeight: true }
        StackLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            currentIndex: espacio.indiceArea
            EspacioEscritura { id: escritura }
            EspacioMetadatos { id: metadatos }
            EspacioPublicacion { id: publicacion }
            EspacioHerramientas { id: herramientas }
        }
    }

    footer: BarraEstado {
        resumen: espacio.resumen
        contexto: espacio.contexto
        tareas: studio.tareas
        onProgresoPulsado: { espacio.fijarArea("herramientas"); herramientas.pestana = 5 }
    }

    // ------------------------------------------------------------------ diálogos
    Kirigami.PromptDialog {
        id: dialogoAplicar
        title: (ops.publica ? "Publicar: " : "Aplicar: ") + ops.titulo + (sitios.hayActual && ops.sobreSitio ? " · " + sitios.nombre : "")
        subtitle: ops.textoConfirmacion + (ops.publica ? "\n\n" + studio.publicacion.textoConfirmacion : "")
        standardButtons: Kirigami.Dialog.Cancel
        customFooterActions: [Kirigami.Action { text: ops.publica ? "Publicar" : "Aplicar"; icon.name: ops.publica ? "cloud-upload" : "dialog-ok-apply"; enabled: ops.puedeAplicar; onTriggered: { ops.aplicar(); dialogoAplicar.close() } }]
        function abrir() {
            if (!ops.puedeAplicar) { ventana.mensajes.mostrar(ops.motivoNoAplicar, "aviso"); return }
            open()
        }
    }
    Kirigami.PromptDialog {
        id: dialogoVenv
        title: "El entorno del studio"
        subtitle: (studio.ajustes.hayVenv ? "Los backends de Python corren con " + studio.ajustes.interprete + " (el .venv del repo: openpyxl, pandas y PyYAML)."
                                           : "No existe el .venv del repo: los backends de metadatos no tienen openpyxl ni pandas y el diagnóstico de metadatos queda vacío.")
                  + "\n\nPara crearlo (sin sudo ni apt):\n" + studio.ajustes.ordenVenv
        standardButtons: Kirigami.Dialog.Close
        customFooterActions: [Kirigami.Action { text: "Copiar la orden"; icon.name: "edit-copy"; onTriggered: { espacio.copiar(studio.ajustes.ordenVenv); dialogoVenv.close() } }]
    }
    DialogoEntrada { id: dialogoEntrada }
    dialogoAjustes: DialogoAjustesStudio {}
}
