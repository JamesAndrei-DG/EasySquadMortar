from PySide6.QtCore import QObject
from core.fastapi_sse import app
import uvicorn


class ObjectFastApi(QObject):
    """Class responsible for initializing and running the FastAPI server."""

    def run_fast_api_server(self) -> None:
        """Runs the FastAPI server."""
        uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)  # might need to change the app to a string
