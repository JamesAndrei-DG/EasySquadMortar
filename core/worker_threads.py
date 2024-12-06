from PySide6.QtCore import QThread, QObject, Signal, Slot
from core.parse_screen import ScreenOCR
from core.fastapi_sse import app
import uvicorn


class ObjectEasyOCR(QObject):
    # Implement a signal to get my data

    def run_EasyOCR(self):
        easyocr = ScreenOCR()
        while True:
            # print(f"NatoMil: {easyocr.get_natomil()}")
            # print(f"Bearing: {easyocr.get_bearing()}")
            pass


class ObjectFastApi(QObject):

    def run_FastApi(self):
        uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)
        pass