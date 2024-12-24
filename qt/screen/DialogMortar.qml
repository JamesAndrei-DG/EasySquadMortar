import QtQuick
import QtQuick.Controls
import QtQuick.Layouts


Dialog {
    id: dialogMortar
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
            ToolTip.visible: hovered
            ToolTip.text: "E01-9-5-3-3"

            validator: RegularExpressionValidator {
                regularExpression: /[a-zA-Z]\d[0-9\-\s]{0,7}/
            }

            onTextEdited: {
                // Convert the text to uppercase
                text = text.toUpperCase();

                // Check if the text length is 3
                if (text.length === 3) {
                    // Validate and modify the third character if it's a space or a hyphen
                    if (text[2] === ' ' || text[2] === '-') {
                        // Create the new text in one step to avoid issues with index assignment
                        text = text[0] + '0' + text[1];
                    }

                } else if (text.length > 3) {
                    if (text.length % 2 === 0 && text.length < 9) {
                        const i = text.length;
                        if (!(text[i - 1] === ' ' || text[i - 1] === '-')) {
                            const character = text[i - 1];
                            text = text.slice(0, text.length - 1);
                            text += '-';
                            text += character;
                        }
                    }
                }
            }
        }
    }

    onAccepted: {
        map_class_py.mortar_position(mortarPosition.text.replace(/--+/g, ''));
        confirmTimer.start();
    }
}