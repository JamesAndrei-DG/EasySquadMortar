import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Controls.Material 2.15

// Set the style globally within QML
QtQuickControls2::Style {
    // Available options: "Material", "Fusion", "Imagine", "Universal", etc.
    name: "Material"  // Change to "Fusion" or others if needed
}

ApplicationWindow {
    visible: true
    width: 640
    height: 480

    Material.theme: Material.Dark // Optional: Set dark theme if using Material style
    Material.accent: Material.Blue

    Column {
        anchors.centerIn: parent
        spacing: 10

        Button {
            text: "Click me"
        }

        Label {
            text: "This is a custom theme!"
        }
    }
}
