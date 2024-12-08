import QtQuick
import QtQuick.Layouts
import QtQuick.Controls


Rectangle {
    id: logoButton
    height: 100
    width: 200
    radius: 10
    color: "grey"
    border.color: "black"
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
                overlayMenu.popup();
                mainWindow.raise();
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


        LogoMenu {
            id: overlayMenu
        }


    }
}