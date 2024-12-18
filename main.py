import sys
import os
from PySide6.QtCore import QUrl, QThread
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWebEngineQuick import QtWebEngineQuick
from core.object_workers import ObjectFastApi, ObjectEasyOCR
from core.map_Qobject import Map
from multiprocessing import freeze_support

def thread_close() -> None:
    """
    Handles the closing operation of the application, including terminating threads
    and ensuring proper cleanup. This function stops and waits for the shutdown of
    the threads used by the application to ensure smooth and safe termination.

    """
    print("Application is closing. Cleaning up...")
    #Stop EasyOcr while loop
    EasyOCR._running = False
    ThreadEasyOCR.terminate()
    ThreadFastAPi.terminate()
    ThreadEasyOCR.wait()
    ThreadFastAPi.wait(2000) #Cant close Uvicorn gracefully
    print("Threads have been stopped.")


if __name__ == "__main__":
    freeze_support()
    # Initialization
    QtWebEngineQuick.initialize()
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    # Handles all FastApi and EasyOCR Logic
    EasyOCR = ObjectEasyOCR()
    FastApi = ObjectFastApi()

    # Threads
    ThreadEasyOCR = QThread()
    ThreadFastAPi = QThread()
    EasyOCR.moveToThread(ThreadEasyOCR)
    FastApi.moveToThread(ThreadFastAPi)
    ThreadEasyOCR.started.connect(EasyOCR.run_easyocr)
    ThreadFastAPi.started.connect(FastApi.run_fast_api_server)
    ThreadEasyOCR.start()
    ThreadFastAPi.start()

    # Map Initialization and logic
    map = Map()
    engine.rootContext().setContextProperty("map_name_list_py", map.get_map_names())
    engine.rootContext().setContextProperty("map_class_py", map)

    # Load QML File

    engine.load((QUrl("qt/root.qml")))

    # Close Thread on Exit
    app.aboutToQuit.connect(thread_close)

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())
