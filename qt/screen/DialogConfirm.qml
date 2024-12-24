import QtQuick
import QtQuick.Controls


Dialog {
    id: dialogConfirm
    x: (parent.width - width) / 2;
    y: (parent.height - height) / 2;

    contentItem: Text {
        text: "Confirm Mortar Position"
        font.pointSize: 12
        font.bold: true
        anchors.top: parent.top
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.topMargin: 8
    }

    standardButtons: Dialog.Ok | Dialog.Cancel;

    onAccepted: {
        map_class_py.location_confirmed();
    }

    onRejected: {
        dialogMortar.open()
    }
}
