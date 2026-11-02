// VistaWeb — la página renderizada en QtWebEngine del sistema (qml6-module-qtwebengine). En archivo aparte: la vista
// previa lo carga con un Loader y, si el módulo falta, muestra el Markdown en su lugar (reingeniería E5).
import QtQuick
import QtWebEngine

WebEngineView {
    id: web
    property url destino
    property int version: 0
    signal navegada(string url)
    url: destino
    onVersionChanged: reload()
    onUrlChanged: navegada(url.toString())
    settings.localContentCanAccessFileUrls: true
    settings.localContentCanAccessRemoteUrls: true
    onNewWindowRequested: request => { web.url = request.requestedUrl }   // los enlaces que abren ventana se quedan aquí
}
