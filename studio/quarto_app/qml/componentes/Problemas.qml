// Problemas — los errores y avisos del último render del sitio actual (de la salida de quarto render, guardada por
// sitio), con su archivo y su línea; Intro abre el archivo.
import QtQuick
import org.kde.kirigami as Kirigami
import GuiComun

ListaDiagnosticos {
    readonly property var s: studio.sitios
    modelo: s.problemasModelo
    // corto (el PlaceholderMessage de la base no lleva explicación aquí): el detalle, en la ayuda de «Renderizar»
    mensajeVacio: !s.hayActual ? "Ningún sitio" : "Sin problemas registrados"
    iconoVacio: "checkmark-symbolic"
    nombreAccesible: "Problemas del render de " + (s.nombre || "ningún sitio")
    onActivada: fila => s.abrirProblema(fila)
}
