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
                property string previousText: ""


                onTextChanged: {
                    let validInput = isValid(text);
                    if (validInput === null) {
                        mortarPosition.text = previousText;
                    } else {
                        mortarPosition.text = validInput;
                        previousText = validInput;
                    }
                }


                function isValid(textinput) {
                    if (textinput.length === 0) return ""; // Allow empty textinput and return an empty string
                    if (textinput[0].match("[0-9]")) return null; // Invalid if the first character is not a letter

                    let textfinal = textinput[0].toUpperCase();





                    // Process the remaining characters
                    for (let i = 1; i < textinput.length; i++) {
                        if (!/^\d$/.test(textinput[i])) return null; // Invalid if not a number

                        textfinal += textinput[i];

                        // Add a dash every two numbers
                        if ((i % 2 === 0) && (i < textinput.length - 1)) {
                            textfinal += "-";
                        }
                    }

                    return textfinal; // Return the formatted valid textinput

                }
            }


        }


        onAccepted: {
            map_class_py.origin_point(mortarPosition.text);
        }


    }
}