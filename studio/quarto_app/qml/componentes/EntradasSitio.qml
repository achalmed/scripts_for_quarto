// EntradasSitio — las entradas del sitio actual (fecha, título, carpeta); elegir una la hace la entrada actual
// («Renderizar la entrada», «Formatear YAML (archivo)»); Intro o doble clic abre su index.qmd.
import QtQuick
import org.kde.kirigami as Kirigami
import GuiComun

TablaDatos {
    readonly property var s: studio.sitios
    modelo: s.entradasModelo
    mensajeVacio: s.hayActual ? "Este sitio no tiene entradas (carpetas AAAA-MM-DD-título con index.qmd)" : "Ningún sitio"
    iconoVacio: "text-markdown"
    columnas: [{ ancho: 7, mono: true }, { ancho: 0, minimo: 10, conIcono: true }, { ancho: 10, secundaria: true, estrecho: true }]
    onFilaActualCambiada: fila => s.fijarEntradaFila(fila)
    onActivada: fila => s.abrirEntradaFila(fila)
}
