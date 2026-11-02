// DialogoAjustesStudio — «Configurar Quarto Studio…»: el puerto del preview, el destino de publicación, el Excel de
// metadatos, la terminal y el intérprete de los backends.
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami
import org.kde.kirigamiaddons.formcard as FormCard
import GuiComun

DialogoAjustes {
    id: dialogo
    title: "Configurar Quarto Studio"
    readonly property var a: studio.ajustes
    modulos: [{ titulo: "General", icono: "configure", pagina: paginaGeneral }]
    onGuardado: { dialogo.a.guardar(); studio.flujo.recargar("entradas"); ventana.mensajes.mostrar("Preferencias guardadas.", "positivo") }

    Component {
        id: paginaGeneral
        ColumnLayout {
            function guardar() { dialogo.a.puerto = parseInt(puerto.text) || 4200; dialogo.a.destino = destino.text; dialogo.a.excel = excel.text; dialogo.a.terminal = terminal.text }
            FormCard.FormHeader { title: "Publicación" }
            FormCard.FormCard {
                FormCard.FormTextFieldDelegate { id: destino; label: "Destino de «Publicar»"; text: dialogo.a.destino; placeholderText: "vacío: git push (Netlify despliega); o netlify, gh-pages…" }
                FormCard.FormTextFieldDelegate { id: puerto; label: "Puerto del preview"; text: String(dialogo.a.puerto); placeholderText: "4200" }
            }
            FormCard.FormHeader { title: "Metadatos" }
            FormCard.FormCard {
                FormCard.FormTextFieldDelegate { id: excel; label: "Excel de metadatos"; text: dialogo.a.excel }
                FormCard.FormTextDelegate { text: "Los backends de Python corren con " + dialogo.a.interprete + (dialogo.a.hayVenv ? " (el .venv del repo)." : ". No existe el .venv del repo: Herramientas › El entorno del studio… dice cómo crearlo.") }
            }
            FormCard.FormHeader { title: "Sistema" }
            FormCard.FormCard {
                FormCard.FormTextFieldDelegate { id: terminal; label: "Terminal para «Abrir terminal aquí»"; text: dialogo.a.terminal; placeholderText: "konsole" }
            }
        }
    }
}
