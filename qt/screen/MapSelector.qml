import QtQuick
import QtQuick.Controls


ComboBox {
    id: mapSelector
    model: map_name_list_py
    opacity: 0.5
    anchors.bottom: parent.bottom
    anchors.right: parent.right
    currentIndex: 0


    onActivated: {
        map_class_py.selected_map(mapSelector.currentIndex);
        mapWindow.map_selected = mapSelector.currentText;
    }


    Component.onCompleted: {
        mapWindow.map_selected = mapSelector.currentText;
        // For scrollable combobox
        mapSelector.popup.contentItem.implicitHeight = Qt.binding(function () {
            return Math.min(250, mapSelector.popup.contentItem.contentHeight);
        });

    }


    background: Rectangle {
        color: "white"
        border.color: "black"
        border.width: 1
        radius: 10  // Rounded corners for ComboBox itself
    }

}