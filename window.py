import sys
import os
from PySide6.QtCore import QUrl, QObject
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, QmlElement
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtQuick import QQuickView
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget
from PySide6.QtCore import Qt
from PySide6.QtWebEngineQuick import QtWebEngineQuick

from PySide6.QtWebEngineWidgets import QWebEngineView

import folium
import io

def test():
    Base_Map = folium.Map(crs='Simple', zoom_start=4)
    data = io.BytesIO()
    Base_Map.save(data, close_file=False)
    webView = QWebEngineView() #can we make it work with qtwebenginequick?
    webView.setHtml(data.getvalue().decode())

    root = engine.rootObjects()[0]
    webViewContainer = root.findChild(QObject, "webViewContainer")

    container = QWidget.createWindowContainer(webView)
    container.setParent(webViewContainer)


if __name__ == "__main__":
    #Initialization
    QtWebEngineQuick.initialize()
    app = QGuiApplication(sys.argv)


    engine = QQmlApplicationEngine()




    #Load Qml
    engine.addImportPath(os.path.join(os.path.dirname(__file__), "qt"))
    engine.load((QUrl("qt/screen/MyRectangle.qml")))



    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())
