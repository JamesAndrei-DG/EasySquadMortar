import QtQuick
import QtQuick.Layouts
import QtQuick.Controls


Menu {
    id: overlayMenu


    MenuItemMortarPos{

    }


    MenuItem {
        text: "Exit"
        onTriggered: Qt.quit()
    }


}