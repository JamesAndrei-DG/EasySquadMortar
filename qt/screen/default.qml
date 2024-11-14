import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import QtQuick.Window
import QtWebEngine

Rectangle {
    width: parent.width
    height: parent.height
    color: "transparent"

    WebEngineView {
        id: webViewContainer
        anchors.fill: parent
        url: Qt.resolvedUrl("test.html")
        opacity: 0.5

        settings {
            javascriptEnabled: true
            localContentCanAccessRemoteUrls: true
        }
    }



    Rectangle {
        id: logobutton
        border.color: "black"
        color: "grey"
        height: 100
        radius: 10
        width: 200
        anchors.top: parent.top
        anchors.right: parent.right



        Text {
            anchors.centerIn: parent
            color: "white"
            text: "Logo PlaceHolder"
        }
        MouseArea {
            anchors.fill: parent
            acceptedButtons: Qt.LeftButton | Qt.RightButton
            property point dragStartPosition

            onPressed: {
                if (mouse.button === Qt.RightButton) { // 'mouse' is a MouseEvent argument passed into the onClicked signal handler
                    overlayMenu.popup()
                } else if (mouse.button === Qt.LeftButton) {
                    dragStartPosition = Qt.point(mouse.x, mouse.y)


                }
            }


            onPositionChanged: function (mouse) {
                if (mouse.buttons & Qt.LeftButton) { // Check if the left mouse button is still pressed
                    var dx = mouse.x - dragStartPosition.x
                    var dy = mouse.y - dragStartPosition.y
                    mainWindow.x += dx
                    mainWindow.y += dy
                }
            }

            Menu{
                id: overlayMenu

                MenuItem{
                    text: "Exit"
                    onTriggered: Qt.quit()
                }

            }
        }
    }
}