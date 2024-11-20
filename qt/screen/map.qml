import QtQuick
import QtWebEngine

WebEngineView {
    id: webViewContainer
    anchors.fill: parent
    url: Qt.resolvedUrl("./maps/" + mapSelector.currentText.replace(" ", "") + ".html")
    opacity: 0.5

    settings {
        javascriptEnabled: true
        localContentCanAccessRemoteUrls: true
    }

}