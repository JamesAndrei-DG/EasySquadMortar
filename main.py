import sys
import os
import re

import PySide6.QtCore
from PySide6.QtCore import QUrl, QObject, Signal, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWebEngineQuick import QtWebEngineQuick
from tools import parse_maps


class maps(QObject):

    def __init__(self):
        QObject.__init__(self)
        self.map_names = []

    def get_map_name(self):
        map_data = parse_maps.parsemaps()

        for i, data in enumerate(map_data):
            self.map_names.append(data[0])
            self.map_names[i] = re.sub(r"(\w)([A-Z])", r"\1 \2", self.map_names[i])

        return self.map_names

    @Slot(str)
    def selected_map(self, message: str):
        print(f"Selected map is: {message}")

    @Slot(str)
    def origin_point(self, location: str):
        print(f"Origin is: {location}")


if __name__ == "__main__":

    # Initialization
    QtWebEngineQuick.initialize()
    app = QGuiApplication(sys.argv)

    engine = QQmlApplicationEngine()

    # Map Class
    map = maps()
    engine.rootContext().setContextProperty("map_name_list_py", map.get_map_name())
    engine.rootContext().setContextProperty("map_class_py", map)

    # Load Qml

    engine.load((QUrl("qt/root.qml")))

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())
