import QtQuick
import QtQuick.Layouts
import QtQuick.Controls


Menu {
    id: overlayMenu


    MenuItemMortarPos{
        id: menuItemMortar
    }


    MenuItem {
        text: "Exit"
        onTriggered: Qt.quit()
    }


}