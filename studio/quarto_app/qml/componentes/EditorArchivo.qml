// EditorArchivo — un documento abierto (reingeniería E4; el de LaTeX Studio, `latex-studio/studio/latex_app/qml/
// componentes/EditorArchivo.qml`, adaptado a Quarto: sin autocompletado de LaTeX ni SyncTeX; candidato a gui-comun):
// TextArea con resaltado de KSyntaxHighlighting (Markdown para .qmd y .md, YAML, BibTeX, SCSS), números de línea y
// comentar líneas según el lenguaje. Cada archivo tiene su TextArea y con él su historial de deshacer. Nunca escribe en
// disco: lo hace Ctrl+S (editor.guardar). Sin colores propios: Kirigami.Theme.
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami

Item {
    id: raiz

    property string ruta: ""
    property string definicion: "Markdown"
    property bool ajustarLineas: true                // la prosa de un .qmd se lee mejor partida
    property real tamanoLetra: 0                     // 0: el de la fuente monoespaciada del tema
    property bool soloLectura: false
    property bool cargado: false
    property bool modificado: false
    property string original: ""                     // el texto como está en disco: modificado = el del editor difiere
    property var inicios: [0]                        // la posición de inicio de cada línea lógica
    property var lineasVisibles: []
    readonly property alias area: area
    readonly property int lineaActual: lineaDe(area.cursorPosition)
    readonly property int columnaActual: area.cursorPosition - (inicios[lineaActual - 1] || 0)
    readonly property bool oscuro: (Kirigami.Theme.backgroundColor.r * 0.299 + Kirigami.Theme.backgroundColor.g * 0.587
                                    + Kirigami.Theme.backgroundColor.b * 0.114) < 0.5


    // ------------------------------------------------------------------ carga y estado
    function cargar() {
        original = studio.editor.leer(ruta)
        area.text = original
        area.cursorPosition = 0
        cargado = true
        modificado = false
        recalcular()
    }
    function recargarDesdeDisco() {
        const pos = area.cursorPosition
        cargar()
        area.cursorPosition = Math.min(pos, area.length)
        studio.editor.aceptarDisco(ruta)
        studio.editor.marcarModificado(ruta, false)
    }
    function guardar(forzar) {
        const r = studio.editor.guardar(ruta, area.text, forzar === true)
        if (r === "") { original = area.text; modificado = false }
        return r
    }
    onModificadoChanged: if (cargado) studio.editor.marcarModificado(ruta, modificado)

    // ------------------------------------------------------------------ líneas
    function recalcular() {
        const t = area.text
        const lista = [0]
        let i = t.indexOf("\n")
        while (i >= 0) { lista.push(i + 1); i = t.indexOf("\n", i + 1) }
        inicios = lista
        visibles()
    }
    function lineaDe(pos) {
        let lo = 0, hi = inicios.length - 1
        while (lo < hi) { const mid = (lo + hi + 1) >> 1; if (inicios[mid] <= pos) lo = mid; else hi = mid - 1 }
        return lo + 1
    }
    function visibles() {
        const flick = desplazamiento.contentItem
        const arriba = flick.contentY, abajo = arriba + desplazamiento.height
        let lo = 0, hi = inicios.length - 1
        while (lo < hi) {
            const mid = (lo + hi) >> 1
            const r = area.positionToRectangle(inicios[mid])
            if (r.y + r.height < arriba) lo = mid + 1; else hi = mid
        }
        const salida = []
        for (let k = lo; k < inicios.length; k++) {
            const r = area.positionToRectangle(inicios[k])
            if (r.y > abajo) break
            salida.push({ n: k + 1, y: r.y - arriba, alto: r.height })
        }
        lineasVisibles = salida
    }
    function irALinea(linea, columna) {
        const n = Math.max(1, Math.min(linea, inicios.length))
        area.cursorPosition = Math.min(area.length, (inicios[n - 1] || 0) + Math.max(0, columna || 0))
        area.forceActiveFocus()
        centrarCursor()
    }
    function centrarCursor() {
        const flick = desplazamiento.contentItem
        const r = area.cursorRectangle
        if (r.y < flick.contentY || r.y + r.height > flick.contentY + desplazamiento.height)
            flick.contentY = Math.max(0, Math.min(flick.contentHeight - desplazamiento.height, r.y - desplazamiento.height / 3))
    }
    function seleccionar(inicio, fin) {
        area.select(inicio, fin)
        centrarCursor()
    }

    // ------------------------------------------------------------------ comentar (Ctrl+T)
    // comentar o descomentar las líneas de la selección, con el comentario del lenguaje
    readonly property var comentario: ({ Markdown: ["<!-- ", " -->"], YAML: ["# ", ""], Lua: ["-- ", ""], SCSS: ["// ", ""],
                                         JavaScript: ["// ", ""], CSS: ["/* ", " */"], HTML: ["<!-- ", " -->"], BibTeX: ["% ", ""] })[definicion] || ["# ", ""]
    function comentar() {
        const ab = comentario[0], ci = comentario[1]
        const a = lineaDe(area.selectionStart), b = lineaDe(Math.max(area.selectionStart, area.selectionEnd - (area.selectionEnd > area.selectionStart ? 1 : 0)))
        let todas = true
        for (let n = a; n <= b; n++) {
            const ini = inicios[n - 1], fin = n < inicios.length ? inicios[n] - 1 : area.length
            const linea = area.getText(ini, fin)
            if (linea.trim() !== "" && !linea.trim().startsWith(ab.trim())) todas = false
        }
        for (let n = b; n >= a; n--) {
            const ini = inicios[n - 1], fin = n < inicios.length ? inicios[n] - 1 : area.length
            const linea = area.getText(ini, fin)
            if (linea.trim() === "") continue
            if (todas) {
                const sangria = linea.length - linea.trimStart().length
                let resto = linea.trimStart().slice(ab.trim().length).replace(/^ /, "")
                if (ci && resto.trimEnd().endsWith(ci.trim())) resto = resto.trimEnd().slice(0, -ci.trim().length).replace(/ $/, "")
                area.remove(ini, fin)
                area.insert(ini, linea.slice(0, sangria) + resto)
            } else {
                area.insert(fin, ci)
                area.insert(ini, ab)
            }
        }
    }

    // ------------------------------------------------------------------ la vista
    RowLayout {
        anchors.fill: parent
        spacing: 0

        // números de línea
        Item {
            id: margen
            Layout.fillHeight: true
            Layout.preferredWidth: metricas.advanceWidth("0") * Math.max(3, String(raiz.inicios.length).length) + Kirigami.Units.largeSpacing * 2
            clip: true
            Accessible.ignored: true
            Rectangle { anchors.fill: parent; color: Kirigami.Theme.alternateBackgroundColor }
            Repeater {
                model: raiz.lineasVisibles
                delegate: QQC2.Label {
                    required property var modelData
                    x: 0
                    y: modelData.y
                    width: margen.width - Kirigami.Units.smallSpacing * 2
                    height: modelData.alto
                    horizontalAlignment: Text.AlignRight
                    verticalAlignment: Text.AlignVCenter
                    text: modelData.n
                    font: area.font
                    color: modelData.n === raiz.lineaActual ? Kirigami.Theme.textColor : Kirigami.Theme.disabledTextColor
                }
            }
        }
        Kirigami.Separator { Layout.fillHeight: true }

        QQC2.ScrollView {
            id: desplazamiento
            Layout.fillWidth: true
            Layout.fillHeight: true
            QQC2.ScrollBar.horizontal.policy: raiz.ajustarLineas ? QQC2.ScrollBar.AlwaysOff : QQC2.ScrollBar.AsNeeded

            QQC2.TextArea {
                id: area
                readOnly: raiz.soloLectura
                textFormat: TextEdit.PlainText
                wrapMode: raiz.ajustarLineas ? TextEdit.Wrap : TextEdit.NoWrap
                font.family: Kirigami.Theme.fixedWidthFont.family
                font.pointSize: raiz.tamanoLetra > 0 ? raiz.tamanoLetra : Kirigami.Theme.fixedWidthFont.pointSize
                selectByMouse: true
                persistentSelection: true
                tabStopDistance: metricas.advanceWidth(" ") * 2
                Accessible.name: "Editor de " + raiz.ruta.split("/").pop()
                background: Rectangle { color: Kirigami.Theme.backgroundColor }

                // el resaltado vuelve a emitir textChanged al engancharse: se compara con lo guardado, no se supone
                onTextChanged: { if (raiz.cargado) raiz.modificado = area.text !== raiz.original; temporizador.restart() }
                onWidthChanged: temporizador.restart()
            }
        }
    }

    Connections {
        target: desplazamiento.contentItem
        function onContentYChanged() { raiz.visibles() }
        function onHeightChanged() { raiz.visibles() }
    }
    Timer { id: temporizador; interval: 60; onTriggered: raiz.recalcular() }
    FontMetrics { id: metricas; font: area.font }

    Loader {
        active: raiz.definicion !== ""
        source: "ResaltadoEditor.qml"
        onLoaded: { item.nombreDefinicion = raiz.definicion; item.oscuro = Qt.binding(() => raiz.oscuro); item.textEdit = area }
    }
}
