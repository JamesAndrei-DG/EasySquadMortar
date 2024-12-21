import sys
import os
from PySide6.QtCore import QUrl, QThread, QObject, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWebEngineQuick import QtWebEngineQuick
from core.Qobject_fastapi import ObjectFastApi
from core.Qobject_map import MapClass
from multiprocessing import freeze_support


def thread_close() -> None:
    """
    Handles the closing operation of the application, including terminating threads
    and ensuring proper cleanup. This function stops and waits for the shutdown of
    the threads used by the application to ensure smooth and safe termination.

    """
    print("Application is closing. Cleaning up...")
    # Stop EasyOcr while loop
    map_container.terminate_easyocr()
    fast_api_container.terminate_server()
    map_thread.quit()
    fast_api_thread.quit()
    map_thread.wait()
    fast_api_thread.wait()  # Cant close Uvicorn gracefully


if __name__ == "__main__":
    freeze_support()
    # Initialization
    QtWebEngineQuick.initialize()
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    # Fast Api thread and logic
    fast_api_container = ObjectFastApi()
    fast_api_thread = QThread()
    fast_api_container.moveToThread(fast_api_thread)
    fast_api_thread.started.connect(fast_api_container.run_fastapi_server)
    # fast_api_thread.start()

    # Map thread and logic
    map_container = MapClass(fast_api_container)
    map_thread = QThread()
    map_container.moveToThread(map_thread)
    map_thread.started.connect(map_container._run_easyocr)
    map_thread.start()

    engine.rootContext().setContextProperty("map_name_list_py", map_container.get_map_names())
    # engine.rootContext().setContextProperty("map_class_py", map_container)

    # Load QML File
    engine.load((QUrl("qt/root.qml")))

    if not engine.rootObjects():
        sys.exit(-1)

    # connect
    # engine.rootObjects()[0].setMortarPos_Signal.connect(map_container.mortar_position, type=Qt.ConnectionType.QueuedConnection)

    engine.rootObjects()[0].rootSignal.connect(map_container.rootest, type=Qt.ConnectionType.QueuedConnection)
    import time
    time.sleep(5)
    qmlmortarpos = engine.rootObjects()[0].findChild(QObject, "inputMortarPosition_objname")

# !!! and connect MyPage2.page2_signal() to test_object.test_slot3
    qmlmortarpos.inputMortarPosition_signal.connect(
        map_container.mortar_position,
        type=Qt.ConnectionType.QueuedConnection)

    # Close Thread on Exit
    app.aboutToQuit.connect(thread_close)

    sys.exit(app.exec())
