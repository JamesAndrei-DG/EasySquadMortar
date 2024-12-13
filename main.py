import sys
import os
from PySide6.QtCore import QUrl, QThread, QProcess
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWebEngineQuick import QtWebEngineQuick
from core.object_workers import ObjectFastApi
from core.map_Qobject import Map

def handle_stderr():
    data = ProcessScreenOCR.readAllStandardError()
    stdout = bytes(data).decode("utf8")
    print(stdout)

def handle_stdout():
    data = ProcessScreenOCR.readAllStandardOutput()
    stdout = bytes(data).decode("utf8")
    print(stdout)

def handle_state(state):
    states = {

        QProcess.NotRunning: 'Not running',
        QProcess.Starting: 'Starting',
        QProcess.Running: 'Running',
    }
    state_name = states[state]
    print(f"State changed: {state_name}")


if __name__ == "__main__":
    # Initialization
    QtWebEngineQuick.initialize()
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    # Thread and Object
    ThreadFastAPi = QThread()
    FastApi = ObjectFastApi()
    FastApi.moveToThread(ThreadFastAPi)
    ThreadFastAPi.started.connect(FastApi.run_fast_api_server)
    ThreadFastAPi.finished.connect(FastApi.deleteLater)

    # ThreadEasyOCR.start()
    ThreadFastAPi.start()

    # QProcess Initialization
    print("----------------------------------------------------------")
    ProcessScreenOCR = QProcess()
    ProcessScreenOCR.readyReadStandardOutput.connect(handle_stdout)
    ProcessScreenOCR.readyReadStandardError.connect(handle_stderr)
    ProcessScreenOCR.stateChanged.connect(handle_state)

    ProcessScreenOCR.start("python3", ['/core/parse_screen.py'])

    # Map Initialization
    map = Map()
    engine.rootContext().setContextProperty("map_name_list_py", map.get_map_names())
    engine.rootContext().setContextProperty("map_class_py", map)

    # Load QML File

    engine.load((QUrl("qt/root.qml")))

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())
