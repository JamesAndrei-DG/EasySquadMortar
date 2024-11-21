import QtQuick
import QtWebEngine

Window {
    id: mapWindow
    color: "white"
    height: 650
    width: 650
    visible: true
    opacity: 0
    flags: Qt.WindowTransparentForInput | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint




    property string map_selected: "AlBasrah"  // Default value

    WebEngineView {
        id: webViewContainer
        anchors.fill: parent
        url: Qt.resolvedUrl("maps/" + mapWindow.map_selected.replace(" ", "") + ".html")
        opacity: 0.5

        settings {
            javascriptEnabled: true
            localContentCanAccessRemoteUrls: true
        }
    }
}