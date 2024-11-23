import QtQuick
import QtQuick.Layouts
import QtQuick.Controls


MenuItem {
    text: "Set Mortar Position"
    onTriggered: inputMortarPosition.open()


    Dialog {
        id: inputMortarPosition
        x: (parent.width - width) / 2
        y: (parent.height - height) / 2
        standardButtons: Dialog.Ok | Dialog.Cancel


        contentItem: ColumnLayout {
            spacing: 10


            Text {
                text: "Set Mortar Position"
                font.pointSize: 12
                font.bold: true
                Layout.alignment: Qt.AlignHCenter
            }


            TextField {
                id: mortarPosition
                focus: true
                placeholderText: "E01-9-5-3-3"
                Layout.fillWidth: true
                font.pointSize: 10
                font.bold: true
                font.family: "Times New Roman"
                inputMask: ">A99-9-9-9-9; "
                ToolTip.visible: hovered
                ToolTip.text: "E01-9-5-3-3"


            }


        }


        onAccepted: {


            map_class_py.origin_point(mortarPosition.text.replace(/--+/g, ''));
        }


    }
}