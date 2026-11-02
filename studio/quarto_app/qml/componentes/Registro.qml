// Registro — la salida íntegra de la última corrida sobre el sitio actual (render, publicación, commit, verificación).
import QtQuick
import GuiComun

VistaTexto {
    readonly property var s: studio.sitios
    texto: s.registro
    definicion: "Bash"
    mensajeVacio: !s.hayActual ? "Ningún sitio" : "Sin registro todavía: lo que se corra sobre " + s.nombre + " (render, publicar, commit, verificar) queda aquí íntegro"
    iconoVacio: "text-x-log"
    nombreAccesible: "Registro de " + (s.nombre || "ningún sitio")
}
