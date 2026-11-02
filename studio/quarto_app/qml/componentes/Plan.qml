// Plan — la última simulación (o el plan de la ventana) de la operación elegida y, debajo, su última aplicación.
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami
import GuiComun

ColumnLayout {
    readonly property var o: studio.operaciones
    spacing: 0
    QQC2.TabBar {
        id: pestanas
        Layout.fillWidth: true
        QQC2.TabButton { text: "Plan" }
        QQC2.TabButton { text: "Registro"; enabled: o.escribe }
    }
    StackLayout {
        Layout.fillWidth: true
        Layout.fillHeight: true
        currentIndex: pestanas.currentIndex
        VistaTexto {
            texto: o.plan
            definicion: "Bash"
            mensajeVacio: !o.hayOperacion ? "Esta vista no tiene operaciones" : "Sin plan todavía: " + o.verbo + " (F5) corre «" + o.titulo + "» sin escribir y deja aquí su salida"
            iconoVacio: "system-run"
            nombreAccesible: "Plan de " + o.titulo
        }
        VistaTexto {
            texto: o.registro
            definicion: "Bash"
            mensajeVacio: o.escribe ? "Sin registro todavía: Aplicar (Ctrl+Intro) corre «" + o.titulo + "» de verdad y deja aquí su salida" : "Esta operación no tiene modo «aplicar»"
            iconoVacio: "dialog-ok-apply"
            nombreAccesible: "Registro de " + o.titulo
        }
    }
}
