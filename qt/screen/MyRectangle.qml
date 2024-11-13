import QtQuick 2.15
import QtQuick.Window 2.15
import QtWebEngine 1.7

Window {
    visible: true
    width: 400
    height: 300
    title: "Red Rectangle Window"

    WebEngineView {
        id: webViewContainer
        anchors.fill: parent
        url: Qt.resolvedUrl("test.html")
    }
}
