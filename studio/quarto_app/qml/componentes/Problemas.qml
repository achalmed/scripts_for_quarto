// Problemas — los errores y avisos del último render del sitio actual (de la salida de quarto render, guardada por
// sitio), con su archivo y su línea; Intro abre el archivo.
import QtQuick
import org.kde.kirigami as Kirigami
import GuiComun

ListaDiagnosticos {
    readonly property var s: studio.sitios
    modelo: s.problemasModelo
    mensajeVacio: !s.hayActual ? "Ningún sitio" : "Sin problemas registrados: «Renderizar» (Ctrl+Intro) deja aquí los errores y avisos de Quarto"
    iconoVacio: "dialog-ok-apply"
    nombreAccesible: "Problemas del render de " + (s.nombre || "ningún sitio")
    onActivada: fila => s.abrirProblema(fila)
}
