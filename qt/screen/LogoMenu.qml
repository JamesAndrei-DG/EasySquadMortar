import QtQuick
import QtQuick.Layouts
import QtQuick.Controls


Menu {
    id: overlayMenu


    MenuItemMortarPos{

    }

    TestItemTargetPos{

    }


    MenuItem {
        text: "Exit"
        onTriggered: Qt.quit()
    }


}