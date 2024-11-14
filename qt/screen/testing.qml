import QtQuick 2.15
import QtQuick.Window 2.15
import QtWebEngine 1.7

Window {
    visible: true
    width: parent.width
    height: parent.height
    title: "Red Rectangle Window"

    WebEngineView {
        id: webViewContainer
        anchors.fill: parent
        url: Qt.resolvedUrl("test.html")

        settings {
            javascriptEnabled: true
            localContentCanAccessRemoteUrls: true
        }
    }
}
