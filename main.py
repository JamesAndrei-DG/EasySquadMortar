import sys
import os
from PySide6.QtCore import QUrl, QThread
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWebEngineQuick import QtWebEngineQuick
from core.worker_Qthreads import ObjectFastApi, ObjectEasyOCR
from core.map_Qobject import Maps

if __name__ == "__main__":

    # Initialization
    QtWebEngineQuick.initialize()
    app = QGuiApplication(sys.argv)

    engine = QQmlApplicationEngine()

    # Qthread
    ThreadEasyOCR = QThread()
    ThreadFastAPi = QThread()
    EasyOCR = ObjectEasyOCR()
    FastApi = ObjectFastApi()
    EasyOCR.moveToThread(ThreadEasyOCR)
    FastApi.moveToThread(ThreadFastAPi)

    ThreadEasyOCR.started.connect(EasyOCR.run_EasyOCR)
    ThreadFastAPi.started.connect(FastApi.run_FastApi)
    ThreadEasyOCR.start()
    ThreadFastAPi.start()

    # Map Class
    map = Maps()
    engine.rootContext().setContextProperty("map_name_list_py", map.get_map_names())
    engine.rootContext().setContextProperty("map_class_py", map)


    # Load Qml

    engine.load((QUrl("qt/root.qml")))

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())
