import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import QtQuick.Window

ApplicationWindow {
    id: mainWindow

    color: "transparent"
    flags: Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint
    height: 650
    width: 1050
    visible: true
    MouseArea {
        anchors.fill: parent
        enabled: false
    }

    Window {
        id: secondWindow
        width: 400
        height: 300
        title: "Second Window"
        color: "transparent"
        visible: true

        Item {
            width: parent.width
            height: parent.height

            Loader {
                id: mapLoader
                anchors.fill: parent
                source: "map.qml"
            }

            MouseArea {
                anchors.fill: parent
                enabled: false
            }
        }

        // Initially set the position of second window relative to the main window
        x: mainWindow.x + 50  // Offset position if needed
        y: mainWindow.y + 50  // Offset position if needed
    }

    // Update position of second window whenever the main window moves
    onXChanged: {
        secondWindow.x = mainWindow.x + 50;  // Adjust the offset as needed
    }

    onYChanged: {
        secondWindow.y = mainWindow.y + 50;  // Adjust the offset as needed
    }

    StackView {
        id: stackView
        anchors.fill: parent
        initialItem: "splash.qml"

        replaceEnter: Transition {
            PropertyAnimation {
                property: "opacity"
                from: 0
                to: 1
                duration: 2000
                easing.type: Easing.InQuart
            }
        }
        replaceExit: Transition {
            PropertyAnimation {
                property: "opacity"
                from: 1
                to: 0
                duration: 500
                easing.type: Easing.InQuad
            }
        }

    }


    Timer {
        id: splashTimer
        interval: 1500
        running: true
        repeat: false

        onTriggered: {
            stackView.replace("default.qml")

            secondDelayTimer.start()


        }
    }
    Timer {
        id: secondDelayTimer
        interval: 520  // Second delay (1 second)
        running: false  // Don't start automatically
        repeat: false  // Ensure it only runs once

        onTriggered: {
            mainWindow.x = Screen.width - mainWindow.width  // Second action
            mainWindow.y = 0
        }
    }


}
