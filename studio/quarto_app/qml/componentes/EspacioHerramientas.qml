// EspacioHerramientas — el área Herramientas: las vistas de la ventana 2.0 (los sitios con su estado, las entradas con el
// Excel, el índice del vault, los índices de contenido), cada una con su tabla, y a la derecha lo de siempre —el
// resumen del sitio, sus entradas, los problemas del último render, la operación elegida con su orden, el plan y el
// registro de la operación— y la salida de la CLI. Las operaciones son las mismas: F5 simula, Ctrl+Intro aplica tras confirmar.
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami
import GuiComun

ColumnLayout {
    id: raiz
    readonly property var espacio: studio.espacio
    readonly property var sitios: studio.sitios
    readonly property var flujo: studio.flujo
    readonly property var ops: studio.operaciones
    readonly property bool enSitios: espacio.vista === "sitios"
    property alias pestana: lado.currentIndex
    function tabla() { return tablas.children[tablas.currentIndex] }
    spacing: 0

    RowLayout {
        Layout.fillWidth: true
        Layout.margins: Kirigami.Units.smallSpacing
        Repeater {
            model: raiz.espacio.vistas
            delegate: QQC2.Button {
                required property var modelData
                text: modelData.texto.replace(" y metadatos", "")
                icon.name: modelData.icono
                checkable: true
                checked: raiz.espacio.vista === modelData.nombre
                flat: !checked
                onClicked: raiz.espacio.fijarVista(modelData.nombre)
            }
        }
        Item { Layout.fillWidth: true }
        QQC2.Label { text: "Operación:"; visible: raiz.ops.lista.length > 0 }
        QQC2.ComboBox {
            id: selector
            visible: raiz.ops.lista.length > 0
            Layout.preferredWidth: Kirigami.Units.gridUnit * 12
            model: raiz.ops.lista
            textRole: "titulo"
            currentIndex: raiz.ops.indiceActual
            onActivated: index => raiz.ops.fijarPorIndice(index)
            Accessible.name: "Operación de la vista"
            Connections { target: raiz.ops; function onListaCambiada() { selector.currentIndex = raiz.ops.indiceActual } }
        }
        BotonAccion { accion: studio.acciones.accion("op.simular") }
        BotonAccion { accion: studio.acciones.accion("op.aplicar") }
    }
    Kirigami.Separator { Layout.fillWidth: true }

    QQC2.SplitView {
        Layout.fillWidth: true
        Layout.fillHeight: true
        StackLayout {
            id: tablas
            QQC2.SplitView.fillWidth: true
            QQC2.SplitView.minimumWidth: Kirigami.Units.gridUnit * 20
            currentIndex: raiz.espacio.indiceVista

            component TablaFlujo: TablaDatos {
                required property string vista
                modelo: raiz.flujo.modeloDe(vista)
                claveAjustes: vista
                umbralEstrecho: Kirigami.Units.gridUnit * 36
                onOrdenar: (columna, descendente) => modelo.ordenar(columna, descendente)
                onFilaActualCambiada: fila => raiz.flujo.fijarFila(vista, fila)
                onActivada: fila => { raiz.flujo.fijarFila(vista, fila); raiz.flujo.abrirElemento() }
            }
            TablaDatos {
                id: tablaSitios
                modelo: raiz.sitios.modelo
                claveAjustes: "sitios"
                umbralEstrecho: Kirigami.Units.gridUnit * 44
                mensajeVacio: raiz.sitios.total === 0 ? "Ningún sitio: el registro _pubs/pubs.yml del hub no se encontró (core/env.py: INDEX_DIR)" : "Ningún sitio cumple el filtro"
                iconoVacio: "folder-html"
                columnas: [{ ancho: 0, minimo: 10, conIcono: true }, { ancho: 12, semantica: true }, { ancho: 5, alinear: "derecha", secundaria: true },
                           { ancho: 6, mono: true, secundaria: true, estrecho: true }, { ancho: 5, alinear: "derecha", secundaria: true, estrecho: true },
                           { ancho: 6, alinear: "derecha", secundaria: true, estrecho: true }, { ancho: 9, secundaria: true, estrecho: true },
                           { ancho: 10, secundaria: true, estrecho: true, visible: false }, { ancho: 14, secundaria: true, estrecho: true, visible: false }]
                onOrdenar: (columna, descendente) => raiz.sitios.modelo.ordenar(columna, descendente)
                onFilaActualCambiada: fila => raiz.sitios.fijarFila(fila)
            }
            TablaFlujo {
                vista: "entradas"
                mensajeVacio: "Ninguna entrada: las entradas son carpetas AAAA-MM-DD-título con index.qmd dentro de los sitios"
                iconoVacio: "text-markdown"
                columnas: [{ ancho: 7, mono: true }, { ancho: 0, minimo: 14, conIcono: true }, { ancho: 9, secundaria: true }, { ancho: 14, secundaria: true, estrecho: true },
                           { ancho: 12, secundaria: true, estrecho: true }, { ancho: 4, semantica: true }]
            }
            TablaFlujo {
                vista: "indice"
                mensajeVacio: "Ningún enlace en web/_indice/: «Sincronizar el índice» los crea por año"
                iconoVacio: "emblem-symbolic-link"
                columnas: [{ ancho: 4, mono: true }, { ancho: 0, minimo: 14, conIcono: true }, { ancho: 5, semantica: true }, { ancho: 18, secundaria: true, estrecho: true }]
            }
            TablaFlujo {
                vista: "contenido"
                mensajeVacio: "Ningún _contenido_*.qmd en los sitios: «Generar los índices del sitio» los escribe por subblog"
                iconoVacio: "view-list-text"
                columnas: [{ ancho: 9 }, { ancho: 12, secundaria: true, estrecho: true }, { ancho: 0, minimo: 12, conIcono: true }, { ancho: 5, alinear: "derecha", secundaria: true },
                           { ancho: 9, secundaria: true, estrecho: true }]
            }
        }
        ColumnLayout {
            QQC2.SplitView.preferredWidth: Kirigami.Units.gridUnit * 28
            QQC2.SplitView.minimumWidth: Kirigami.Units.gridUnit * 18
            spacing: 0
            QQC2.TabBar {
                id: lado
                Layout.fillWidth: true
                currentIndex: 3
                QQC2.TabButton { text: raiz.enSitios ? "Resumen" : "Elemento"; width: implicitWidth }
                QQC2.TabButton { text: "Entradas"; width: implicitWidth; enabled: raiz.enSitios }
                QQC2.TabButton { text: "Problemas" + (raiz.sitios.nProblemas > 0 ? " · " + raiz.sitios.nProblemas : ""); width: implicitWidth; enabled: raiz.enSitios }
                QQC2.TabButton { text: "Operación"; width: implicitWidth }
                QQC2.TabButton { text: "Plan"; width: implicitWidth }
                QQC2.TabButton { text: "Salida"; width: implicitWidth }
            }
            StackLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                currentIndex: lado.currentIndex
                StackLayout {
                    currentIndex: raiz.enSitios ? 0 : (raiz.espacio.vista === "entradas" ? 1 : 2)
                    ResumenSitio {}
                    Metadatos {}
                    Elemento {}
                }
                EntradasSitio {}
                Problemas {}
                Operacion {}
                Plan {}
                PanelInferior { consola: studio.consola }
            }
        }
    }
}
