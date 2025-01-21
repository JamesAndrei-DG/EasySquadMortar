import sys
import os
from PySide6.QtCore import QUrl, QThread, QObject, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWebEngineQuick import QtWebEngineQuick
from core.Qobject_fastapi import ObjectFastApi
from core.Qobject_map import MapClass
from multiprocessing import freeze_support

def check_components():
    if os.path.exists("qt/components/maps/AlBasrah.html"):
        print("File Found")
    else:
        import tool_generate_html


def check_resolution(application:any) -> None:
    # Check Resolution
    import ctypes

    width, height = application.primaryScreen().size().toTuple()

    if (width, height) not in [(1920, 1080),]:
        ctypes.windll.user32.MessageBoxW(0,
                                         f"Your screen resolution of:\n{width}x{height} is not yet supported\nUse 1920x1080\n\nNote: If you are using the correct resolution\nMake sure your scaling is set to 100% only",
                                         f"Resolution not supported!", 0)
        raise Exception("Invalid Monitor Size")

def thread_close() -> None:
    """
    Handles the closing operation of the application, including terminating threads
    and ensuring proper cleanup. This function stops and waits for the shutdown of
    the threads used by the application to ensure smooth and safe termination.

    """
    print("Application is closing. Cleaning up...")
    # Stop EasyOcr while loop
    map_container.stop_threads_and_tasks()
    fast_api_container.terminate_server()
    map_thread.quit()
    fast_api_thread.quit()
    print("Waiting for map_thread to close")
    map_thread.wait()
    print("map_thread to closed successfully")
    print("Waiting for fast_api_thread to close")
    fast_api_thread.wait(5000)  # Cant close Uvicorn gracefully
    print("fast_api_thread to closed successfully")


if __name__ == "__main__":
    freeze_support()
    check_components()

    # Initialization
    QtWebEngineQuick.initialize()
    app = QGuiApplication(sys.argv)
    check_resolution(app)

    engine = QQmlApplicationEngine()

    # Fast Api thread and logic
    fast_api_container = ObjectFastApi()
    fast_api_thread = QThread()
    fast_api_container.moveToThread(fast_api_thread)
    fast_api_thread.started.connect(fast_api_container.run_fastapi_server)
    fast_api_thread.start()

    # Map thread and logic
    map_container = MapClass(fast_api_container)
    map_thread = QThread()
    map_container.moveToThread(map_thread)
    map_thread.started.connect(map_container._run_easyocr)
    map_thread.start()

    engine.rootContext().setContextProperty("map_name_list_py", map_container.get_map_names())
    engine.rootContext().setContextProperty("map_class_py", map_container)

    # Load QML File
    engine.load((QUrl("qt/root.qml")))

    if not engine.rootObjects():
        sys.exit(-1)

    # Close Thread on Exit
    app.aboutToQuit.connect(thread_close)

    sys.exit(app.exec())
