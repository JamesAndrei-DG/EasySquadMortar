import QtQuick
import QtQuick.Layouts
import QtQuick.Controls


Menu {
    id: overlayMenu


    Menuitemmortarpos{

    }


    MenuItem {
        text: "Exit"
        onTriggered: Qt.quit()
    }


}