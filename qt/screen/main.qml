import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import QtQuick.Window


Rectangle {
    width: parent.width
    height: parent.height
    color: "transparent"

    LogoEntry {
        id: logoEntry
    }

    MapSelector {
        id: mapSelector
    }
}