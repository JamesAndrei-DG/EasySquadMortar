import QtQuick
import QtQuick.Layouts
import QtQuick.Controls


Rectangle {
    id: logoEntry
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

    MouseFunction {
        id: mouseFunction
    }


    LogoMenu {
        id: logoMenu
    }

    DialogConfirm {
        id: dialogConfirm
    }

    DialogMortar {
        id: dialogMortar
    }

    Timer {
        id: confirmTimer
        interval: 250
        running: false
        repeat: false

        onTriggered: {
            dialogConfirm.open()
        }
    }
}