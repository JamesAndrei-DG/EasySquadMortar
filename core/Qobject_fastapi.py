from PySide6.QtCore import QObject
import core.fastapi_sse as fastapi
import uvicorn


class ObjectFastApi(QObject):
    """Class responsible for initializing and running the FastAPI server."""

    def __init__(self):
        super().__init__()
        self.server = None

    def run_fastapi_server(self) -> None:
        """Runs the FastAPI server."""
        config = uvicorn.Config(fastapi.app, host="127.0.0.1", port=8000,
                                reload=False)  # might need to change the app to a string
        self.server = uvicorn.Server(config=config)
        self.server.run()

    def change_xy(self, coordinates: tuple[int, int]) -> None:
        fastapi.long, fastapi.lat = coordinates[0], -coordinates[1]

    def pause_sending_coordinates(self) -> None:
        fastapi.pause()

    def resume_sending_coordinates(self) -> None:
        fastapi.resume()

    def terminate_server(self) -> None:
        if self.server:
            fastapi.running = False
            self.server.should_exit = True
            print("Server is shutting down")
        else:
            print(
                "Cannot terminate: No server is currently running or the server has already been terminated.")
