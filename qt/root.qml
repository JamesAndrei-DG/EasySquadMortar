import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import QtQuick.Window

import "components"


ApplicationWindow {
    id: mainWindow

    color: "transparent"
    flags:  Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
    height: 128 //650
    width: 500 //1050
    visible: true


    StackView {
        id: stackView
        anchors.fill: parent
        initialItem: "screen/splash.qml"

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
                to: 1
                duration: 500
                easing.type: Easing.InQuad
            }

        }

    }


    PropertyAnimation {
        id: opacityAnimation
        target: mapWindow
        property: "opacity"
        from: 0
        to: 0.75
        duration: 2000  // Duration of the fade-out effect
        easing.type: Easing.InQuart  // Ease-in quad effect
    }


    Timer {
        id: splashTimer
        interval: 1500
        running: true
        repeat: false

        onTriggered: {
            stackView.replace("screen/main.qml")

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

            opacityAnimation.start()
        }

    }

    QtObject {
        property Window child: Mapwindow {
            id: mapWindow
            // Position mapWindow relative to mainWindow
            x: mainWindow.x - (mapWindow.width - mainWindow.width)  // Offset if you want mapWindow to be positioned relative to mainWindow
            y: mainWindow.y   // Offset if you want mapWindow to be positioned relative to mainWindow
        }

    }

}
