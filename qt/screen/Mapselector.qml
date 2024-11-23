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
        map_class_py.selected_map(mapSelector.currentText);
        mapWindow.map_selected = mapSelector.currentText;
    }


    Component.onCompleted: {
        mapWindow.map_selected = mapSelector.currentText;
        map_class_py.selected_map(mapSelector.currentText);
        mapSelector.popup.contentItem.implicitHeight = Qt.binding(function () {
            return Math.min(250, mapSelector.popup.contentItem.contentHeight);
        });
    }


}