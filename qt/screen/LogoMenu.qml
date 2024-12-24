import QtQuick
import QtQuick.Controls


Menu {
    id: logoMenu

    MenuItem {
        text: "Set Mortar Position"
        onTriggered: dialogMortar.open()
    }

    MenuItem {
        text: "Exit"
        onTriggered: Qt.quit()
    }
}