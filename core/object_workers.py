from PySide6.QtCore import QObject
from core.parse_screen import ParseScreen
from core.fastapi_sse import app
import uvicorn


class ObjectEasyOCR(QObject):
    """Class responsible for running EasyOCR in a loop."""

    def run_easyocr(self) -> None:
        """Runs the EasyOCR process."""
        easyocr = ParseScreen()
        while True:
            NatoMil = easyocr.get_natomil()
            Azimuth = easyocr.get_azimuth()

            # print(f"NatoMil: {easyocr.get_natomil()}")
            # print(f"Azimuth: {easyocr.get_azimuth()}")


class ObjectFastApi(QObject):
    """Class responsible for initializing and running the FastAPI server."""

    def run_fast_api_server(self) -> None:
        """Runs the FastAPI server."""
        uvicorn.run(app, host="127.0.0.1", port=8000, reload=False) #might need to change the app to a string
