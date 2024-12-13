from PySide6.QtCore import QObject
import core.parse_screen as screenparser
from core.fastapi_sse import app
import uvicorn


class ObjectEasyOCR(QObject):
    """Class responsible for running EasyOCR in a loop."""
    def __init__(self):
        self.parser = screenparser

    def run_easyocr(self) -> None:
        """Runs the EasyOCR process."""
        print(f"-------------------------------------------------------------------------")
        print(f"parsing on another process")
        self.parser.parse_it_on_another_process()

    def __del__(self):
        self.parser.deleteprocess()



class ObjectFastApi(QObject):
    """Class responsible for initializing and running the FastAPI server."""


    def run_fast_api_server(self) -> None:
        """Runs the FastAPI server."""

        print(f"-------------------------------------------------------------------------")
        print(f"fastapi")
        uvicorn.run(app, host="127.0.0.1", port=8000, reload=False) #might need to change the app to a string
