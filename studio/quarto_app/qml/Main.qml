// Main.qml — Quarto Studio (reingeniería del 2026-11-02, docs/reingenieria.md; la forma de escritor aprobada el
// 2026-11-18): un entorno de escritura y publicación de la familia de sitios Quarto sobre GuiComun.VentanaBase, en tres
// paneles de escritor. Arriba, las cuatro áreas (Escribir · Metadatos · Publicación · Herramientas, Ctrl+1–4), el sitio
// con su estado de construcción, el botón principal «Renderizar este archivo» (Ctrl+Mayús+K, N 5.16), el sitio entero
// (Ctrl+Mayús+B) y Publicar. A la izquierda, el árbol de sitios y entradas. En el centro, el área: el .qmd con su YAML
// resaltado y la vista previa tal como saldrá publicada; el diagnóstico de metadatos; la vista de publicación; las tablas
// y operaciones de siempre. Abajo, el estado del render y los sitios con cambios sin publicar. Ninguna llamada al disco
// ni a un backend aquí: todo lo hacen los controladores de Python (studio.*). Sin colores propios: Kirigami.Theme.
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
    function abrirEnLinea(ruta, linea) { if (!ruta) return; espacio.fijarArea("escribir"); escritura.abrir(ruta, linea || 0) }

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
            case "antes_de_publicar": dialogoPublicar.abrir(); break
            case "ayuda_ia": dialogoAyuda.abrir(escritura.editorActual); break
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
            // un render del sitio con problemas lleva a ellos; el del archivo deja al escritor donde está (la franja de abajo los cuenta)
            if (aplicar && (id === "render" || id === "render_entrada") && sitios.nProblemas > 0) { espacio.fijarArea("herramientas"); herramientas.pestana = 2 }
            else if (ventana.area === "herramientas") herramientas.pestana = 4
        }
    }

    // ------------------------------------------------------------------ la cabecera
    header: QQC2.ToolBar {
        position: QQC2.ToolBar.Header
        contentItem: RowLayout {
            spacing: Kirigami.Units.smallSpacing
            // las cuatro áreas: el selector segmentado de la base (el pozo con sus píldoras; ← → con el teclado)
            SelectorSegmentado {
                titulo: "Áreas"
                opciones: espacio.areas.map((a, i) => ({ clave: a.nombre, texto: a.texto, icono: a.icono, atajo: "Ctrl+" + (i + 1) }))
                actual: espacio.area
                onElegida: clave => espacio.fijarArea(clave)
            }
            Item { Layout.fillWidth: true }
            // el sitio y su estado de construcción (EtiquetaNivel de la base: el color es el semántico del tema)
            QQC2.Label {
                visible: sitios.hayActual
                text: sitios.nombre
                font.weight: Font.DemiBold
            }
            EtiquetaNivel {
                id: etiquetaEstado
                visible: sitios.hayActual
                text: sitios.estadoTexto
                nivel: sitios.estadoNivel
                QQC2.ToolTip.text: sitios.motivo
                QQC2.ToolTip.visible: zonaEstado.hovered
                HoverHandler { id: zonaEstado }
                Accessible.name: "Sitio " + sitios.nombre + ": " + sitios.estadoTexto
            }
            Kirigami.Separator { Layout.fillHeight: true; Layout.margins: Kirigami.Units.smallSpacing }
            // el botón principal (N 5.16): se renderiza el archivo, nunca el sitio a ciegas
            BotonPrincipal {
                id: renderArchivo
                accion: ventana.accion("sitio.renderizar_archivo")
                text: "Renderizar este archivo"
                QQC2.ToolTip.text: (studio.documentos.actual ? "Renderiza " + studio.documentos.relActual + " y recarga la vista previa"
                                                             : "Abre un documento del sitio para renderizarlo") + " (" + accion.atajoTexto + ")"
                QQC2.ToolTip.visible: hovered
                QQC2.ToolTip.delay: Kirigami.Units.toolTipDelay
            }
            BotonAccion { accion: ventana.accion("sitio.renderizar"); conTexto: false }
            QQC2.ToolButton {
                text: "Publicar"
                icon.name: "cloud-upload-symbolic"
                enabled: sitios.hayActual
                onClicked: espacio.fijarArea("publicacion")
                QQC2.ToolTip.text: "La vista de publicación: a dónde va el sitio y qué lleva"
                QQC2.ToolTip.visible: hovered
            }
            BotonAccion { accion: ventana.accion("ventana.paleta"); conTexto: false }
        }
    }

    // ------------------------------------------------------------------ árbol · área · franja del render
    ColumnLayout {
        anchors.fill: parent
        spacing: 0
        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 0
            PanelProyectos {
                id: proyectos
                Layout.preferredWidth: Kirigami.Units.gridUnit * 17
                Layout.minimumWidth: Kirigami.Units.gridUnit * 14
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
        BarraRender {
            id: barraRender
            Layout.fillWidth: true
            onIrAPublicacion: nombre => { sitios.fijarPorNombre(nombre); espacio.fijarArea("publicacion") }
            onVerProblemas: ventana.accion("sitio.problemas").disparar()
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
        subtitle: ops.textoConfirmacion + (ops.publica ? "\n\n" + studio.publicacion.textoConfirmacion
                  + (studio.entrega.resumenEntradas ? "\n\nAntes de publicar: " + studio.entrega.resumenEntradas + "." : "") : "")
        standardButtons: Kirigami.Dialog.Cancel
        showCloseButton: false            // ya hay botones al pie: sin la × del encabezado
        customFooterActions: [Kirigami.Action { text: ops.publica ? "Publicar" : "Aplicar"; icon.name: ops.publica ? "cloud-upload" : "dialog-ok-apply"; enabled: ops.puedeAplicar; onTriggered: { ops.aplicar(); dialogoAplicar.close() } }]
        function abrir() {
            if (!ops.puedeAplicar) { ventana.mensajes.mostrar(ops.motivoNoAplicar, "pista"); return }   // el motivo, 6 s en la barra de estado
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
        showCloseButton: false            // ya hay botones al pie: sin la × del encabezado
        customFooterActions: [Kirigami.Action { text: "Copiar la orden"; icon.name: "edit-copy"; onTriggered: { espacio.copiar(studio.ajustes.ordenVenv); dialogoVenv.close() } }]
    }
    DialogoEntrada { id: dialogoEntrada }
    DialogoAntesDePublicar { id: dialogoPublicar }
    DialogoAyudaIA { id: dialogoAyuda }
    dialogoAjustes: DialogoAjustesStudio {}
}
