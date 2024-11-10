import sys
import os
from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, QmlElement
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtQuick import QQuickView
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import Qt







if __name__ == "__main__":
    #Initialization
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()


    #Load Qml
    engine.addImportPath(os.path.join(os.path.dirname(__file__), "qt"))
    engine.load((QUrl("qt/screen/main.qml")))

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())
