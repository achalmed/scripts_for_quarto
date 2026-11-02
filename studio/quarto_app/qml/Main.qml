// Main.qml — Quarto Studio: el hub y los doce sitios de la familia, sus entradas y el flujo render → publicar en un
// espacio de trabajo al estilo Dolphin/Kate sobre GuiComun.VentanaStudio. Navegación (Sitios por estado · Flujo) ·
// centro (la tabla de la vista) · detalles (el sitio: Resumen, Entradas, Problemas, Registro; la entrada: Metadatos; el
// elemento; la operación: Operación, Plan) · panel inferior (la salida de la CLI) · barra de estado. Ninguna llamada
// al disco ni a un backend aquí: todo lo hacen los controladores de Python (studio.*).
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami
import GuiComun
import "componentes"

VentanaStudio {
    id: ventana

    readonly property var espacio: studio.espacio
    readonly property var registro: studio.acciones
    readonly property var sitios: studio.sitios
    readonly property var flujo: studio.flujo
    readonly property var ops: studio.operaciones
    readonly property string vista: espacio.vista
    readonly property int indice: espacio.indiceVista
    readonly property bool enSitios: vista === "sitios"
    readonly property bool elementoDeAqui: flujo.hayElemento && flujo.vistaElemento === vista

    title: espacio.textoVista + " — Quarto Studio"
    acciones: registro
    tareas: studio.tareas
    consola: studio.consola
    descripcion: descripcionStudio
    autor: "Edison Achalma (@achalmed)"
    resumen: espacio.resumen
    contexto: espacio.contexto
    claveAjustes: "ventana"

    function accion(nombre) { return registro.accion(nombre) }
    function tablaActual() { return centro.children[ventana.indice] }
    function irAPestana(i) { ventana.mostrarDetalles = true; detalles.pestanaActual = i }
    function pestanaInicial() {
        switch (ventana.vista) {
        case "sitios": return 0
        case "entradas": return ventana.elementoDeAqui ? 4 : 6
        default: return ventana.elementoDeAqui ? 5 : 6
        }
    }
    function religarNavegacion() {
        navegacion.actual = Qt.binding(() => ventana.enSitios ? (espacio.filtro === "todos" ? "sitios" : "sitios." + espacio.filtro) : ventana.vista)
    }

    Connections {
        target: studio.interfaz
        function onPedir(nombre, datos) {
            switch (nombre) {
            case "filtrar": filtro.forceActiveFocus(); filtro.selectAll(); break
            case "seleccionar_todo": { const t = tablaActual(); if (t && t.seleccionarTodo) t.seleccionarTodo(); break }
            case "seleccionar_fila": { const t = tablaActual(); if (t && datos.fila >= 0) t.seleccionarFila(datos.fila, true); break }
            case "aplicar": dialogoAplicar.abrir(); break
            case "nueva_entrada": dialogoEntrada.abrir(); break
            case "venv": dialogoVenv.open(); break
            case "pestana": irAPestana(datos.indice); break
            case "paleta": ventana.paleta.abrir(datos.texto || ""); break
            }
        }
    }
    Connections { target: espacio; function onAviso(texto, tipo) { ventana.mensajes.mostrar(texto, tipo) } }
    Connections { target: sitios; function onAviso(texto, tipo) { ventana.mensajes.mostrar(texto, tipo) } function onSeleccionar(fila) { if (fila >= 0) tablaSitios.seleccionarFila(fila, true); irAPestana(0) } }
    Connections { target: flujo; function onAviso(texto, tipo) { ventana.mensajes.mostrar(texto, tipo) } }
    Connections {
        target: ops
        function onAviso(texto, tipo) { ventana.mensajes.mostrar(texto, tipo) }
        function onTerminada(id, aplicar, codigo) {
            if (aplicar && (id === "render" || id === "render_entrada") && sitios.nProblemas > 0) irAPestana(2)
            else if (aplicar && ventana.enSitios) irAPestana(3)
            else if (!aplicar) irAPestana(7)
        }
    }
    Connections { target: espacio; function onVistaCambiada() { filtro.text = ""; religarNavegacion(); irAPestana(pestanaInicial()) } function onFiltroCambiado() { religarNavegacion() } }

    // ------------------------------------------------------------------ barra: la operación de la vista y el filtro
    herramientasExtra: [
        QQC2.ComboBox {
            id: selectorOperacion
            visible: ops.lista.length > 0
            Layout.preferredWidth: Kirigami.Units.gridUnit * 16
            model: ops.lista
            textRole: "titulo"
            currentIndex: ops.indiceActual
            onActivated: index => ops.fijarPorIndice(index)
            Accessible.name: "Operación de la vista"
            QQC2.ToolTip.text: ops.descripcion
            QQC2.ToolTip.visible: hovered && ops.descripcion !== ""
            Connections { target: ops; function onListaCambiada() { selectorOperacion.currentIndex = ops.indiceActual } }
        },
        Kirigami.SearchField {
            id: filtro
            Layout.preferredWidth: Kirigami.Units.gridUnit * 11
            placeholderText: "Filtrar (Ctrl+F)"
            onTextChanged: { const t = tablaActual(); if (t && t.modelo && t.modelo.filtrar) t.modelo.filtrar(text) }
            Keys.onEscapePressed: { text = ""; const t = tablaActual(); if (t) t.forceActiveFocus() }
            Accessible.name: "Filtrar"
        }
    ]

    // ------------------------------------------------------------------ navegación
    navegacion: PanelNavegacion {
        id: navegacion
        secciones: [
            { titulo: "Sitios", filas: sitios.filasNavegacion },
            { titulo: "Flujo", filas: sitios.filasFlujo.concat(flujo.filasNavegacion) }
        ]
        onElegida: nombre => {
            if (nombre === "flujo.render") { espacio.fijarVista("sitios"); espacio.fijarFiltro("sin_render"); ops.fijar("render") }
            else if (nombre === "flujo.publicar") { espacio.fijarVista("sitios"); espacio.fijarFiltro("sin_publicar"); ops.fijar("publicar") }
            else if (nombre.startsWith("sitios")) { espacio.fijarVista("sitios"); espacio.fijarFiltro(nombre.length > 6 ? nombre.substring(7) : "todos") }
            else espacio.fijarVista(nombre)
            religarNavegacion()
        }
        Component.onCompleted: religarNavegacion()
    }

    // ------------------------------------------------------------------ centro
    centro: StackLayout {
        id: centro
        currentIndex: ventana.indice

        component MenuSitio: MenuAcciones {
            acciones: ventana.registro
            conAtajos: false
            elementos: [
                { tipo: "accion", nombre: "op.render" }, { tipo: "accion", nombre: "op.publicar" }, { tipo: "accion", nombre: "op.commit" }, { tipo: "accion", nombre: "op.preview" },
                { tipo: "separador" },
                { tipo: "accion", nombre: "op.simular" }, { tipo: "accion", nombre: "op.aplicar" },
                { tipo: "separador" },
                { tipo: "accion", nombre: "sitio.nueva_entrada" }, { tipo: "accion", nombre: "sitio.entradas" }, { tipo: "accion", nombre: "sitio.problemas" },
                { tipo: "separador" },
                { tipo: "accion", nombre: "archivo.navegador" }, { tipo: "accion", nombre: "archivo.carpeta" }, { tipo: "accion", nombre: "archivo.terminal" }, { tipo: "accion", nombre: "archivo.copiar" }
            ]
        }
        component MenuElemento: MenuAcciones {
            acciones: ventana.registro
            conAtajos: false
            elementos: [
                { tipo: "accion", nombre: "archivo.abrir" }, { tipo: "accion", nombre: "archivo.carpeta" }, { tipo: "accion", nombre: "archivo.copiar" },
                { tipo: "separador" },
                { tipo: "accion", nombre: "op.simular" }, { tipo: "accion", nombre: "op.aplicar" },
                { tipo: "separador" },
                { tipo: "accion", nombre: "ver.releer" }
            ]
        }
        component TablaFlujo: TablaDatos {
            required property string vista
            modelo: flujo.modeloDe(vista)
            claveAjustes: vista
            umbralEstrecho: Kirigami.Units.gridUnit * 36
            onOrdenar: (columna, descendente) => modelo.ordenar(columna, descendente)
            onFilaActualCambiada: fila => flujo.fijarFila(vista, fila)
            onActivada: fila => { flujo.fijarFila(vista, fila); flujo.abrirElemento() }
            menuContextual: MenuElemento {}
        }

        TablaDatos {                                              // 0 · Sitios
            id: tablaSitios
            modelo: sitios.modelo
            claveAjustes: "sitios"
            umbralEstrecho: Kirigami.Units.gridUnit * 44
            mensajeVacio: sitios.total === 0 ? "Ningún sitio: el registro _pubs/pubs.yml del hub no se encontró (core/env.py: INDEX_DIR)"
                                             : "Ningún sitio cumple el filtro «" + espacio.textoFiltro + "»"
            iconoVacio: "folder-html"
            columnas: [
                { ancho: 0, minimo: 10, conIcono: true },
                { ancho: 12, semantica: true },
                { ancho: 5, alinear: "derecha", secundaria: true },
                { ancho: 6, mono: true, secundaria: true, estrecho: true },
                { ancho: 5, alinear: "derecha", secundaria: true, estrecho: true },
                { ancho: 6, alinear: "derecha", secundaria: true, estrecho: true },
                { ancho: 9, secundaria: true, estrecho: true },
                { ancho: 10, secundaria: true, estrecho: true, visible: false },
                { ancho: 14, secundaria: true, estrecho: true, visible: false }
            ]
            onOrdenar: (columna, descendente) => sitios.modelo.ordenar(columna, descendente)
            onFilaActualCambiada: fila => sitios.fijarFila(fila)
            onActivada: fila => { sitios.fijarFila(fila); irAPestana(0) }
            menuContextual: MenuSitio {}
        }
        TablaFlujo {                                              // 1 · Entradas y metadatos
            vista: "entradas"
            mensajeVacio: "Ninguna entrada: las entradas son carpetas AAAA-MM-DD-título con index.qmd dentro de los sitios"
            iconoVacio: "text-markdown"
            columnas: [{ ancho: 7, mono: true }, { ancho: 0, minimo: 14, conIcono: true }, { ancho: 9, secundaria: true }, { ancho: 14, secundaria: true, estrecho: true },
                       { ancho: 12, secundaria: true, estrecho: true }, { ancho: 4, semantica: true }]
        }
        TablaFlujo {                                              // 2 · Índice del vault
            vista: "indice"
            mensajeVacio: "Ningún enlace en web/_indice/: «Sincronizar el índice» los crea por año"
            iconoVacio: "emblem-symbolic-link"
            columnas: [{ ancho: 4, mono: true }, { ancho: 0, minimo: 14, conIcono: true }, { ancho: 5, semantica: true }, { ancho: 18, secundaria: true, estrecho: true }]
        }
        TablaFlujo {                                              // 3 · Índices de contenido
            vista: "contenido"
            mensajeVacio: "Ningún _contenido_*.qmd en los sitios: «Generar los índices del sitio» los escribe por subblog"
            iconoVacio: "view-list-text"
            columnas: [{ ancho: 9 }, { ancho: 12, secundaria: true, estrecho: true }, { ancho: 0, minimo: 12, conIcono: true }, { ancho: 5, alinear: "derecha", secundaria: true },
                       { ancho: 9, secundaria: true, estrecho: true }]
        }
    }

    // ------------------------------------------------------------------ detalles
    detalles: PanelDetalles {
        id: detalles
        anchoPreferido: Kirigami.Units.gridUnit * 26
        anchoMinimo: Kirigami.Units.gridUnit * 18
        titulo: ventana.enSitios ? (sitios.hayActual ? sitios.nombre : "")
                                 : (ventana.elementoDeAqui ? flujo.elementoTitulo : (ops.hayOperacion ? ops.titulo : espacio.textoVista))
        subtitulo: ventana.enSitios ? (sitios.hayActual ? (sitios.tema + (sitios.dominio ? " · " + sitios.dominio.replace("https://", "").replace(/\/$/, "") : "")) : "")
                                    : (ventana.elementoDeAqui ? flujo.elementoSubtitulo : "")
        icono: ventana.enSitios ? "folder-html" : ""
        mensajeVacio: "Elige un sitio en la tabla: su estado, sus entradas, los problemas de su último render y su registro"
        iconoVacio: "folder-html"
        accionesCabecera: ventana.enSitios ? [ventana.accion("archivo.navegador"), ventana.accion("archivo.carpeta"), ventana.accion("archivo.terminal")]
                                           : [ventana.accion("archivo.abrir"), ventana.accion("archivo.carpeta")]
        pestanas: [
            { titulo: "Resumen", visible: ventana.enSitios || ventana.vista === "contenido" },
            { titulo: "Entradas", contador: sitios.nEntradas, visible: ventana.enSitios },
            { titulo: "Problemas", contador: sitios.nProblemas, visible: ventana.enSitios },
            { titulo: "Registro", visible: ventana.enSitios },
            { titulo: "Metadatos", contador: flujo.nDiferencias, visible: ventana.vista === "entradas" },
            { titulo: "Elemento", visible: ventana.vista === "indice" || ventana.vista === "contenido" },
            { titulo: "Operación", visible: ops.lista.length > 0 },
            { titulo: "Plan", visible: ops.lista.length > 0 }
        ]
        ResumenSitio {}
        EntradasSitio {}
        Problemas {}
        Registro {}
        Metadatos {}
        Elemento {}
        Operacion {}
        Plan {}
        Component.onCompleted: ventana.irAPestana(ventana.pestanaInicial())
    }

    inferior: PanelInferior { consola: studio.consola }

    // ------------------------------------------------------------------ diálogos
    Kirigami.PromptDialog {
        id: dialogoAplicar
        title: (ops.publica ? "Publicar: " : "Aplicar: ") + ops.titulo + (sitios.hayActual && ops.sobreSitio ? " · " + sitios.nombre : "")
        subtitle: ops.textoConfirmacion
        standardButtons: Kirigami.Dialog.Cancel
        customFooterActions: [Kirigami.Action { text: ops.publica ? "Publicar" : "Aplicar"; icon.name: ops.publica ? "cloud-upload" : "dialog-ok-apply"; enabled: ops.puedeAplicar; onTriggered: { ops.aplicar(); dialogoAplicar.close() } }]
        function abrir() {
            if (!ops.puedeAplicar) { ventana.mensajes.mostrar(ops.motivoNoAplicar, "aviso"); irAPestana(6); return }
            open()
        }
    }
    Kirigami.PromptDialog {
        id: dialogoVenv
        title: "El entorno del studio"
        subtitle: (studio.ajustes.hayVenv ? "Los backends de Python corren con " + studio.ajustes.interprete + " (el .venv del repo: openpyxl, pandas y PyYAML)."
                                           : "No existe el .venv del repo: los backends de metadatos no tienen openpyxl ni pandas y la columna «Excel» queda vacía.")
                  + "\n\nPara crearlo (sin sudo ni apt):\n" + studio.ajustes.ordenVenv
        standardButtons: Kirigami.Dialog.Close
        customFooterActions: [Kirigami.Action { text: "Copiar la orden"; icon.name: "edit-copy"; onTriggered: { espacio.copiar(studio.ajustes.ordenVenv); dialogoVenv.close() } }]
    }
    DialogoEntrada { id: dialogoEntrada }
    dialogoAjustes: DialogoAjustesStudio {}
}
