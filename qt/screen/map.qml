import QtQuick
import QtWebEngine

WebEngineView {
    id: webViewContainer
    anchors.fill: parent
    url: "file://" + Qt.resolvedUrl("./maps/" + mainWindow.selectedMap.replace(" ", "") + ".html") // Bind URL to main window's selected map
    opacity: 0.5

    settings {
        javascriptEnabled: true
        localContentCanAccessRemoteUrls: true
    }

    MouseArea {
        anchors.fill: parent
        enabled: false
    }
}
