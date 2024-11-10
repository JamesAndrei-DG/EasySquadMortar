import QtQuick 2.15
import QtQuick.Window 2.15

Window {
    visible: true
    width: 400
    height: 300
    title: "Red Rectangle Window"

    Rectangle {
        width: 200
        height: 100
        color: "red"
        anchors.centerIn: parent
    }
}
