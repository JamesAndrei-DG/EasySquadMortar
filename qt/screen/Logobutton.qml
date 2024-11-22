import QtQuick
import QtQuick.Layouts
import QtQuick.Controls

Rectangle {
    id: logoButton
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

        Menu {
            id: overlayMenu

            MenuItem {
                text: "Set Mortar Position"
                onTriggered: inputMortarPosition.open()

                Dialog {
                    id: inputMortarPosition

                    x: (parent.width - width) / 2
                    y: (parent.height - height) / 2


                    title: "Set Mortar Position"
                    standardButtons: Dialog.Ok | Dialog.Cancel


                    TextField {
                        id: mortarPosition
                        focus: true
                        placeholderText: "E01-9-5-4-..."
                        Layout.fillWidth: true
                        font.pointSize: 12
                        font.bold: true
                        font.family: "Times New Roman"
                        color: "red"
                    }
                }
            }


            MenuItem {
                text: "Exit"
                onTriggered: Qt.quit()
            }

        }
    }
}