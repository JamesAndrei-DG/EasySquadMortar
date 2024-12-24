import QtQuick
import QtQuick.Controls

MouseArea {
    id: mouseFunction
    anchors.fill: parent
    acceptedButtons: Qt.LeftButton | Qt.RightButton
    property point dragStartPosition

    function mouseclick(mouse) {
        if (mouse.button === Qt.RightButton) { // 'mouse' is a MouseEvent argument passed into the onClicked signal handler
            logoMenu.popup();
        } else if (mouse.button === Qt.LeftButton) {
            dragStartPosition = Qt.point(mouse.x, mouse.y)
        }
    }

    function mousemove(mouse) {
        if (mouse.buttons & Qt.LeftButton) { // Check if the left mouse button is still pressed
            var dx = mouse.x - dragStartPosition.x
            var dy = mouse.y - dragStartPosition.y
            mainWindow.x += dx
            mainWindow.y += dy
        }
    }

    onPressed: (mouse) => {
        mouseclick(mouse);
    }

    onPositionChanged: (mouse) => {
        mousemove(mouse);
    }
}