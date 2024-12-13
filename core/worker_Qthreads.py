from PySide6.QtCore import QObject
from core.parse_screen import ScreenOCR
from core.fastapi_sse import app
import uvicorn


class ObjectEasyOCR(QObject):
    """Class responsible for running EasyOCR in a loop."""

    def run_easyocr(self) -> None:
        """Runs the EasyOCR process."""
        easyocr = ScreenOCR()
        while True:
            # For Debugging Purposes
            # print(f"NatoMil: {easyocr.get_natomil()}")
            # print(f"Bearing: {easyocr.get_bearing()}")
            pass


class ObjectFastApi(QObject):
    """Class responsible for initializing and running the FastAPI server."""

    def run_fast_api_server(self) -> None:
        """Runs the FastAPI server."""
        uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)
