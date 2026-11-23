// DialogoAyudaIA — «Ayuda de la IA para la entrada…» (Ctrl+Alt+A; plan «aprender y enseñar», fase 4.5): el ciclo de la
// ayuda por parte de LaTeX Studio sobre un post. Tres pasos: elegir qué se pide (una sección, la introducción, los
// metadatos o la auditoría editorial) y copiar el prompt de posts con la entrada; pegar lo que respondió el chat; ver el
// cambio sugerido y ponerlo en el editor (en el cursor o en lugar de lo seleccionado; los metadatos, en lugar del
// frontmatter). Ctrl+Z lo deshace y el archivo se escribe solo con Ctrl+S. Poner en el editor (o, en la auditoría,
// «Registrar el uso») deja el uso en _ia/registro.yml del post, que pide «Antes de publicar». Antes de copiar, la ventana
// revisa si el prompt lleva datos de estudiantes o del despacho (C12.3) y, si los lleva, copiar queda a decisión del autor.
// La lección de un curso (curso: y tema: en el frontmatter) tiene su modo, con el prompt 05/05 y el esqueleto de
// leccion.py. Si la entrada no incluye todavía _ia/declaracion.md, una casilla ofrece ponerlo al final al aceptar.
// Ningún modelo se llama desde aquí: todo es studio.ayuda.
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami
import GuiComun

Kirigami.Dialog {
    id: dialogo
    readonly property var a: studio.ayuda
    property var editor: null                   // el EditorTexto de la entrada abierta
    property string modo: "seccion"
    property string seleccion: ""               // lo seleccionado al abrir (el borrador de la sección)
    property int cursor: 0
    property var prompt: null                   // {prompt, modo, nombre, pone, fuente, aviso, largo} o {error}
    property var pegado: null                   // {ok, errores, avisos, pone, antes, despues, diff}
    property var revision: null                 // {sensible, nivel, hallazgos, porque, fuente}
    property bool esperando: false
    property bool revisando: false
    readonly property var declaracion: editor ? a.incluirDeclaracion(editor.area.text) : null   // {texto, cambiado, linea}

    title: "Ayuda de la IA" + (prompt && prompt.nombre ? " — " + prompt.nombre : "")
    preferredWidth: Kirigami.Units.gridUnit * 44
    preferredHeight: Kirigami.Units.gridUnit * 38
    standardButtons: Kirigami.Dialog.Close
    showCloseButton: false            // ya hay botones al pie: sin la × del encabezado

    function abrir(e) {
        if (!a.disponible) { ventana.mensajes.mostrar(a.motivo, "pista"); return }
        if (!e) { ventana.mensajes.mostrar("Abre en Escribir la entrada que quieres trabajar.", "aviso"); return }
        editor = e; seleccion = e.area.selectedText || ""; cursor = e.area.cursorPosition
        prompt = null; pegado = null; revision = null; respuesta.text = ""
        pedir(seleccion ? "seccion" : modo)
        open()
    }
    function pedir(clave) {
        modo = clave; prompt = null; pegado = null; revision = null; esperando = true
        a.pedirPrompt(clave, editor.area.text, seleccion)
    }
    function copiar() { a.copiar(prompt.prompt); ventana.mensajes.mostrar("Prompt copiado: pégalo en tu chat.", "positivo") }
    function registrar(parte) {
        const f = prompt && prompt.fuente ? prompt.fuente : {}
        a.registrar(modo, f, prompt ? prompt.prompt || "" : "", parte || "")
    }

    Connections {
        target: dialogo.a
        function onPromptListo(p) { dialogo.esperando = false; dialogo.prompt = p }
        function onPegadoListo(r) { dialogo.esperando = false; dialogo.pegado = r }
        function onPromptRevisado(r) { dialogo.revisando = false; dialogo.revision = r; if (!r.sensible) dialogo.copiar() }
        function onRegistrado(r) {
            if (r.error) ventana.mensajes.mostrar("El uso no se registró: " + r.error, "error")
            else if (r.escrito) ventana.mensajes.mostrar("Uso de la IA registrado en " + r.registro + ": la entrada debe incluir "
                                                         + r.declaracion + " para «Antes de publicar».", "positivo")
        }
    }

    customFooterActions: [
        Kirigami.Action {
            text: "Copiar el prompt"; icon.name: "edit-copy"
            enabled: !!dialogo.prompt && !!dialogo.prompt.prompt && !dialogo.revisando
            onTriggered: { dialogo.revisando = true; dialogo.revision = null; dialogo.a.revisarPrompt(dialogo.prompt.entrada || "") }
        },
        Kirigami.Action {
            text: "Comprobar lo pegado"; icon.name: "dialog-ok"
            enabled: respuesta.text.trim() !== "" && !dialogo.esperando && !!dialogo.editor
            onTriggered: { dialogo.esperando = true; dialogo.a.comprobar(dialogo.modo, respuesta.text, dialogo.editor.area.text, dialogo.seleccion) }
        },
        Kirigami.Action {
            text: dialogo.pegado && dialogo.pegado.pone === "nada" ? "Registrar el uso" : "Poner en el editor"
            icon.name: dialogo.pegado && dialogo.pegado.pone === "nada" ? "document-save" : "document-edit"
            enabled: !!dialogo.pegado && dialogo.pegado.ok === true && !!dialogo.editor && (dialogo.pegado.pone === "nada" || !dialogo.editor.soloLectura)
            onTriggered: {
                const r = dialogo.pegado
                if (r.pone !== "nada") {
                    const area = dialogo.editor.area
                    let i = r.antes ? area.text.indexOf(r.antes) : (r.pone === "frontmatter" ? 0 : Math.min(dialogo.cursor, area.text.length))
                    if (r.pone === "frontmatter" && r.antes && i !== 0) i = -1
                    if (i < 0) { ventana.mensajes.mostrar("La entrada cambió en el editor desde que lo comprobaste: vuelve a comprobarlo.", "aviso"); return }
                    if (r.antes) area.remove(i, i + r.antes.length)
                    area.insert(i, r.despues)
                    dialogo.editor.seleccionar(i, i + r.despues.length)
                }
                if (incluir.visible && incluir.checked && !dialogo.editor.soloLectura) {
                    const ar = dialogo.editor.area, linea = dialogo.declaracion.linea
                    ar.insert(ar.text.length, (ar.text.endsWith("\n\n") ? "" : ar.text.endsWith("\n") ? "\n" : "\n\n") + linea + "\n")
                }
                dialogo.registrar("")
                ventana.mensajes.mostrar(r.pone === "nada" ? "Uso registrado: corrige la entrada con lo que aceptes."
                                                           : "Cambio puesto en el editor: revísalo y guarda con Ctrl+S (Ctrl+Z lo deshace).", "positivo")
                dialogo.close()
            }
        }
    ]

    QQC2.ScrollView {
        id: vista
        contentWidth: availableWidth
        QQC2.ScrollBar.horizontal.policy: QQC2.ScrollBar.AlwaysOff
        ColumnLayout {
            x: Kirigami.Units.largeSpacing
            width: vista.availableWidth - Kirigami.Units.largeSpacing * 2
            spacing: Kirigami.Units.smallSpacing

            // 1. qué se pide y el prompt
            Kirigami.Heading { level: 4; text: "1. Elige qué pides y copia el prompt" }
            Flow {
                Layout.fillWidth: true
                spacing: Kirigami.Units.smallSpacing
                Repeater {
                    model: dialogo.a.modos
                    OpcionColor {
                        required property var modelData
                        text: modelData.nombre
                        elegida: dialogo.modo === modelData.clave
                        onClicked: dialogo.pedir(modelData.clave)
                        QQC2.ToolTip.text: modelData.descripcion
                        QQC2.ToolTip.visible: hovered
                        QQC2.ToolTip.delay: Kirigami.Units.toolTipDelay
                    }
                }
            }
            QQC2.Label {
                Layout.fillWidth: true
                visible: dialogo.esperando && !dialogo.prompt
                text: "Preparando el prompt de la entrada…"
                color: Kirigami.Theme.disabledTextColor
            }
            Kirigami.InlineMessage {
                Layout.fillWidth: true
                visible: !!dialogo.prompt && !!dialogo.prompt.error
                type: Kirigami.MessageType.Warning
                text: dialogo.prompt && dialogo.prompt.error ? dialogo.prompt.error : ""
            }
            QQC2.Label {
                Layout.fillWidth: true
                visible: !!dialogo.prompt && !dialogo.prompt.error
                wrapMode: Text.WordWrap
                text: dialogo.prompt && dialogo.prompt.fuente ? "«" + dialogo.prompt.fuente.titulo + "»" + (dialogo.prompt.fuente.version ? ", versión " + dialogo.prompt.fuente.version : "")
                      + (dialogo.seleccion && dialogo.prompt.pone === "cursor" ? " · con lo seleccionado como borrador" : "") : ""
                color: Kirigami.Theme.disabledTextColor
            }
            QQC2.Label {
                Layout.fillWidth: true
                visible: text !== ""
                wrapMode: Text.WordWrap
                text: dialogo.prompt ? (dialogo.prompt.aviso || "") + (dialogo.prompt.largo ? " El prompt es largo para un chat externo." : "") : ""
                color: Kirigami.Theme.neutralTextColor
            }
            // el aviso antes de copiar (C12.3)
            Kirigami.InlineMessage {
                id: avisoSensible
                Layout.fillWidth: true
                visible: !!dialogo.revision && dialogo.revision.sensible === true
                type: dialogo.revision && dialogo.revision.nivel === "alto" ? Kirigami.MessageType.Error : Kirigami.MessageType.Warning
                text: !dialogo.revision ? "" : dialogo.revision.error ? "No se pudo revisar el prompt (" + dialogo.revision.error + "). ¿Lo copias igual?"
                      : "El prompt parece llevar datos que no deben salir de la máquina: "
                        + (dialogo.revision.hallazgos || []).slice(0, 4).map(h => h.tipo + (h.linea > 0 ? " (línea " + h.linea + ")" : "")).join(", ")
                        + ((dialogo.revision.total || 0) > 4 ? " y " + (dialogo.revision.total - 4) + " más" : "") + ". Quítalos antes de pegarlo en un chat externo."
                actions: [
                    Kirigami.Action { text: "Copiar de todos modos"; icon.name: "edit-copy"; onTriggered: { dialogo.revision = null; dialogo.copiar() } },
                    Kirigami.Action { text: "No copiar"; icon.name: "dialog-cancel"; onTriggered: dialogo.revision = null }
                ]
            }
            QQC2.Label {
                Layout.fillWidth: true
                visible: avisoSensible.visible && text !== ""
                text: dialogo.revision ? [(dialogo.revision.porque || "").replace(/\.$/, ""), dialogo.revision.fuente].filter(x => !!x).join(" · ") : ""
                wrapMode: Text.WordWrap
                font: Kirigami.Theme.smallFont
                color: Kirigami.Theme.disabledTextColor
            }

            // 2. lo pegado
            Kirigami.Heading { level: 4; text: "2. Pega aquí la respuesta del chat"; visible: !!dialogo.prompt && !dialogo.prompt.error }
            QQC2.TextArea {
                id: respuesta
                Layout.fillWidth: true
                Layout.minimumHeight: Kirigami.Units.gridUnit * 7
                visible: !!dialogo.prompt && !dialogo.prompt.error
                wrapMode: TextEdit.Wrap
                placeholderText: dialogo.prompt && dialogo.prompt.pone === "frontmatter" ? "El bloque ```yaml con el frontmatter que devolvió el chat"
                                 : dialogo.prompt && dialogo.prompt.pone === "nada" ? "Los hallazgos que devolvió el chat" : "El bloque ```markdown que devolvió el chat"
                font: Kirigami.Theme.fixedWidthFont
                Accessible.name: "Respuesta del chat"
                onTextChanged: dialogo.pegado = null
            }

            // 3. el cambio sugerido
            Repeater {
                model: dialogo.pegado ? (dialogo.pegado.errores || []) : []
                Kirigami.InlineMessage { required property string modelData; Layout.fillWidth: true; visible: true; type: Kirigami.MessageType.Error; text: modelData }
            }
            Repeater {
                model: dialogo.pegado ? dialogo.pegado.avisos || [] : []
                Kirigami.InlineMessage { required property string modelData; Layout.fillWidth: true; visible: true; type: Kirigami.MessageType.Warning; text: modelData }
            }
            Kirigami.Heading {
                level: 4
                visible: !!dialogo.pegado && dialogo.pegado.ok === true
                text: dialogo.pegado && dialogo.pegado.pone === "nada" ? "3. Corrige tú la entrada con lo que aceptes" : "3. El cambio sugerido"
            }
            QQC2.TextArea {
                Layout.fillWidth: true
                Layout.minimumHeight: Kirigami.Units.gridUnit * 8
                visible: !!dialogo.pegado && dialogo.pegado.ok === true
                readOnly: true
                text: !dialogo.pegado ? "" : dialogo.pegado.pone === "nada" ? dialogo.pegado.resto || "" : dialogo.pegado.diff || dialogo.pegado.despues || ""
                font: Kirigami.Theme.fixedWidthFont
                wrapMode: dialogo.pegado && dialogo.pegado.pone === "nada" ? TextEdit.Wrap : TextEdit.NoWrap
                Accessible.name: "Cambio sugerido"
            }
            QQC2.CheckBox {
                id: incluir
                Layout.fillWidth: true
                visible: !!dialogo.pegado && dialogo.pegado.ok === true && !!dialogo.declaracion && dialogo.declaracion.cambiado
                         && !!dialogo.editor && !dialogo.editor.soloLectura
                checked: true
                text: "Incluir al final de la entrada " + (dialogo.declaracion ? dialogo.declaracion.linea : "")
                      + " (la declaración del uso de la IA que pide «Antes de publicar»)"
            }
        }
    }
}
