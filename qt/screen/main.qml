import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import QtQuick.Window


Rectangle {
    width: parent.width
    height: parent.height
    color: "transparent"


    ColumnLayout {
        spacing: 2


        Rectangle {
            Layout.preferredWidth: 50
            Layout.preferredHeight: 60
            color: "white"


            TextField {
                id: textField
                width: 300
                height: 40
                placeholderText: "Enter text (A + numbers)"
                font.pixelSize: 16


                onTextChanged: {
                    let validInput = isValidInput(text);
                    if (validInput === null) {
                        textField.text = previousText;
                        isValid = false;
                    } else {
                        textField.text = validInput;
                        previousText = validInput;
                        isValid = true;
                    }
                }


                property string previousText: ""
                property bool isValid: true


                function isValidInput(input) {
                    if (input.length === 0) return ""; // Allow empty input and return an empty string
                    // Ensure the first character is a letter and convert it to uppercase
                    let formattedInput = input[0].toUpperCase();
                    if (!/^[A-Za-z]$/.test(input[0])) return null; // Invalid if the first character is not a letter


                    // Process the remaining characters
                    for (let i = 1; i < input.length; i++) {
                        if (!/^\d$/.test(input[i])) return null; // Invalid if not a number

                        formattedInput += input[i];

                        // Add a dash every two numbers
                        if ((i % 2 === 0) && (i < input.length - 1)) {
                            formattedInput += "-";
                        }
                    }

                    return formattedInput; // Return the formatted valid input


                }
            }
        }
    }


    MapSelector {
        id: mapSelector
    }


    LogoButton {
        id: logoButton
    }


}