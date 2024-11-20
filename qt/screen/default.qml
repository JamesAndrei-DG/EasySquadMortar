import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import QtQuick.Window


Rectangle {
    width: parent.width
    height: parent.height
    color: "transparent"
    MouseArea {
        anchors.fill: parent
        enabled: false
    }


    //Load Map




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

        property string selectedMap: "defaultMap" // Initial map selection

        ComboBox {
            id: mapSelector
            model: mapNameList
            opacity: 0.5
            anchors.bottom: parent.bottom
            anchors.right: parent.right
            currentIndex: 0
            onActivated: {
                selectedMap = mapSelector.currentText  // Update selected map text
                secondWindow.url = "file://" + Qt.resolvedUrl("./maps/" + selectedMap.replace(" ", "") + ".html") // Update second window URL dynamically
            }

            Component.onCompleted: {
                mapSelector.popup.contentItem.implicitHeight = Qt.binding(function () {
                    return Math.min(250, mapSelector.popup.contentItem.contentHeight);
                });
            }

        }
    }


    Rectangle {
        id: logoButton
        border.color: "black"
        color: "grey"
        height: 100
        radius: 10
        width: 200
        anchors.top: parent.top
        anchors.right: parent.right


        Text {
            anchors.centerIn: parent
            color: "white"
            text: "Logo PlaceHolder"
        }
        MouseArea {
            anchors.fill: parent
            acceptedButtons: Qt.LeftButton | Qt.RightButton
            property point dragStartPosition

            onPressed: {
                if (mouse.button === Qt.RightButton) { // 'mouse' is a MouseEvent argument passed into the onClicked signal handler
                    overlayMenu.popup()
                } else if (mouse.button === Qt.LeftButton) {
                    dragStartPosition = Qt.point(mouse.x, mouse.y)


                }
            }


            onPositionChanged: function (mouse) {
                if (mouse.buttons & Qt.LeftButton) { // Check if the left mouse button is still pressed
                    var dx = mouse.x - dragStartPosition.x
                    var dy = mouse.y - dragStartPosition.y
                    mainWindow.x += dx
                    mainWindow.y += dy
                }
            }

            Menu {
                id: overlayMenu

                MenuItem {
                    text: "Exit"
                    onTriggered: Qt.quit()
                }

            }
        }
    }
}