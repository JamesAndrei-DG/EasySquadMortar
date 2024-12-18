from PySide6.QtCore import QObject
import core.parse_screen as screenparser
from core.fastapi_sse import app
import uvicorn
from multiprocessing import Value, Process
import ctypes


class ObjectEasyOCR(QObject):
    """Class responsible for running EasyOCR in a loop."""

    def __init__(self):
        super().__init__()
        # Initialize Varibles
        self.natomil = Value(ctypes.c_uint16)
        self.azimuth = Value(ctypes.c_float)
        self._pause = Value(ctypes.c_bool) #To be implemented
        self._running = True

    def run_easyocr(self) -> None:
        """
        Runs the EasyOCR process in a separate thread and manages its lifecycle. This method
        sets up a multiprocessing Process to execute the screen parsing function.

        Attributes:
            azimuth: The azimuth value passed to the screen parsing function.
            natomil: The natomil value passed to the screen parsing function.
            _running: A flag that indicates whether the instance is in a running state.
        """
        # Parse the screen on another process
        # Make sure "freeze_support()" is used
        parser_process = Process(target=screenparser.parse_my_screen, args=(self.azimuth, self.natomil))
        parser_process.start()

        import time
        while self._running:
            time.sleep(3)
        print("Terminating EasyOcr Process")
        # Exits after termination
        parser_process.terminate()
        parser_process.join()
        parser_process.close()
        print("Termination Successful")


class ObjectFastApi(QObject):
    """Class responsible for initializing and running the FastAPI server."""

    def run_fast_api_server(self) -> None:
        """Runs the FastAPI server."""
        uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)  # might need to change the app to a string
