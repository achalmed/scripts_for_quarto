// ResumenSitio — el sitio actual: carpeta, repo, dominio, tema; el estado por la regla de la puerta R6 y su motivo;
// rama, fuentes sin confirmar, commits por empujar, último render y último commit de fuentes; entradas y problemas.
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami
import GuiComun

QQC2.ScrollView {
    id: pagina
    readonly property var s: studio.sitios
    function colorEstado(nivel) {
        switch (nivel) {
        case "positivo": return Kirigami.Theme.positiveTextColor
        case "neutro": return Kirigami.Theme.neutralTextColor
        case "negativo": return Kirigami.Theme.negativeTextColor
        case "activo": return Kirigami.Theme.activeTextColor
        default: return Kirigami.Theme.textColor
        }
    }
    contentWidth: availableWidth
    QQC2.ScrollBar.horizontal.policy: QQC2.ScrollBar.AlwaysOff
    ColumnLayout {
        width: pagina.availableWidth - Kirigami.Units.largeSpacing * 2
        x: Kirigami.Units.largeSpacing
        y: Kirigami.Units.largeSpacing
        spacing: Kirigami.Units.largeSpacing
        Kirigami.PlaceholderMessage {
            Layout.fillWidth: true
            visible: !pagina.s.hayActual
            text: "Ningún sitio"
            explanation: "Elige un sitio en la tabla o en una entrada de la vista Entradas."
            icon.name: "folder-html"
        }
        Kirigami.FormLayout {
            visible: pagina.s.hayActual
            Layout.fillWidth: true
            QQC2.Label { Kirigami.FormData.label: "Estado:"; text: pagina.s.estadoTexto; color: pagina.colorEstado(pagina.s.estadoNivel); font.bold: true }
            QQC2.Label { Kirigami.FormData.label: "Por qué:"; text: pagina.s.motivo; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            Kirigami.Separator { Kirigami.FormData.isSection: true; Kirigami.FormData.label: "El sitio" }
            QQC2.Label { Kirigami.FormData.label: "Carpeta:"; text: pagina.s.rutaCorta; wrapMode: Text.WrapAnywhere; Layout.fillWidth: true; color: Kirigami.Theme.disabledTextColor }
            QQC2.Label { Kirigami.FormData.label: "Repositorio:"; visible: pagina.s.repo !== ""; text: pagina.s.repo; font: Kirigami.Theme.fixedWidthFont }
            QQC2.Label { Kirigami.FormData.label: "Dominio:"; visible: pagina.s.dominio !== ""; text: pagina.s.dominio; wrapMode: Text.WrapAnywhere; Layout.fillWidth: true }
            QQC2.Label { Kirigami.FormData.label: "Tema:"; text: pagina.s.tema || "—" }
            QQC2.Label { Kirigami.FormData.label: "Proyecto Quarto:"; text: pagina.s.hayQuartoYml ? "_quarto.yml" : "sin _quarto.yml"; color: pagina.s.hayQuartoYml ? Kirigami.Theme.textColor : Kirigami.Theme.negativeTextColor }
            QQC2.Label { Kirigami.FormData.label: "Render:"; text: pagina.s.haySite ? "_site/index.html" : "sin _site/index.html"; color: pagina.s.haySite ? Kirigami.Theme.textColor : Kirigami.Theme.negativeTextColor }
            Kirigami.Separator { Kirigami.FormData.isSection: true; Kirigami.FormData.label: "Git" }
            QQC2.Label { Kirigami.FormData.label: "Rama:"; text: pagina.s.hayGit ? pagina.s.rama : "no es un repositorio"; font: pagina.s.hayGit ? Kirigami.Theme.fixedWidthFont : Kirigami.Theme.defaultFont }
            QQC2.Label { Kirigami.FormData.label: "Fuentes sin confirmar:"; visible: pagina.s.hayGit; text: pagina.s.cambios > 0 ? pagina.s.cambios : "ninguna"; color: pagina.s.cambios > 0 ? Kirigami.Theme.neutralTextColor : Kirigami.Theme.textColor }
            QQC2.Label { Kirigami.FormData.label: "Por empujar:"; visible: pagina.s.hayGit; text: pagina.s.porEmpujar; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            QQC2.Label { Kirigami.FormData.label: "Último render confirmado:"; visible: pagina.s.hayGit; text: pagina.s.fechaRender }
            QQC2.Label { Kirigami.FormData.label: "Último commit de fuentes:"; visible: pagina.s.hayGit; text: pagina.s.fechaFuentes }
            Kirigami.Separator { Kirigami.FormData.isSection: true; Kirigami.FormData.label: "Contenido" }
            QQC2.Label { Kirigami.FormData.label: "Entradas:"; text: pagina.s.nEntradas + " (pestaña Entradas)" }
            QQC2.Label { Kirigami.FormData.label: "Último render:"; text: pagina.s.resumenProblemas || "sin registro en esta ventana"; color: pagina.s.nProblemas > 0 ? Kirigami.Theme.neutralTextColor : Kirigami.Theme.textColor; wrapMode: Text.WordWrap; Layout.fillWidth: true }
        }
        Flow {
            visible: pagina.s.hayActual
            Layout.fillWidth: true
            spacing: Kirigami.Units.smallSpacing
            BotonAccion { accion: studio.acciones.accion("archivo.navegador"); conTexto: false }
            BotonAccion { accion: studio.acciones.accion("sitio.nueva_entrada"); conTexto: false }
            BotonAccion { accion: studio.acciones.accion("op.preview") }
            BotonAccion { accion: studio.acciones.accion("op.publicar") }
            QQC2.Button {
                readonly property var a: studio.acciones.accion("op.render")
                highlighted: true
                text: a.textoPlano; icon.name: "run-build"; enabled: a.habilitada
                onClicked: a.disparar()
                QQC2.ToolTip.text: "Elige «Renderizar» como operación: F5 muestra el plan, Ctrl+Intro renderiza"; QQC2.ToolTip.visible: hovered
            }
        }
        Item { Layout.preferredHeight: Kirigami.Units.largeSpacing }
    }
}
