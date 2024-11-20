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
