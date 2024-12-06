from PySide6.QtCore import QThread, QObject, Signal, Slot
from core.parse_screen import ScreenOCR


class ObjectEasyOCR(QObject):
    # Implement a signal to get my data

    def run_EasyOCR(self):
        easyocr = ScreenOCR()
        while True:
            print(f"NatoMil: {easyocr.get_natomil()}")
            print(f"Bearing: {easyocr.get_bearing()}")
