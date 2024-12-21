import ctypes
import re
import time
from multiprocessing import Process, Value
from threading import Event, Thread

from PySide6.QtCore import QObject, Signal, Slot

import core.parse_screen as screenparser
from core.Qobject_fastapi import ObjectFastApi
from core.map_functions import MapFunction
from core.parse_maps import parse_maps


class MapClass(QObject):
    keypad_received = Signal(str)

    def __init__(self, fastapi: ObjectFastApi) -> None:

        super().__init__()
        # Initialize Map Manager
        self.map_manager = MapFunction()
        self.map_names = []
        self.map_data = parse_maps()
        self.target_keypad = ''
        self.natomil = Value(ctypes.c_uint16, 0)
        self.azimuth = Value(ctypes.c_float, 0.0)
        self._running = True
        self._pause = Event()
        self._pause.set()
        self.thread_mortar = None
        self.thread_computation = None
        self.process_parser = None
        self.fastapi_reference = fastapi  # we dont check if fastapi is valid

    def get_map_names(self):
        """
        Parses and formats the map names from the loaded map data.
        """
        for i, data in enumerate(self.map_data):
            self.map_names.append(data[0])
            self.map_names[i] = re.sub(r"(\w)([A-Z])|_", r"\1 \2", self.map_names[i])

        return self.map_names

    @Slot(int)
    def selected_map(self, map_index: int):
        """
        Handles user selection of a map.
        """
        try:
            print(f"Selected map index: {map_index}")
            self.map_manager.change_map(map_index)
        except Exception as error:  # Added exception handling
            print(f"Error encountered when selecting map: {error}")

    @Slot(str)
    def mortar_position(self, keypad: str):
        """
        Sets the mortar's origin using the given keypad.
        Executes the action in a new thread.
        """
        print(f"Origin is: {keypad}")
        if self.thread_mortar and self.thread_mortar.is_alive():
            self.thread_mortar.join()

        self.thread_mortar = Thread(target=self.map_manager.set_origin_keypad, args=(keypad,))
        self.thread_mortar.start()

        if not self.thread_computation or not self.thread_computation.is_alive():
            self._run_computation_thread()

    def _run_computation_thread(self) -> None:
        self.thread_computation = Thread(target=self._compute_location)
        self.thread_computation.start()

    def _compute_location(self) -> None:
        while self._running:
            self._pause.wait()
            natomil = int(self.natomil.value)
            azimuth = float(self.azimuth.value)
            if natomil == 0 or azimuth == -1:
                time.sleep(0.5)
                continue

            coordinates = self.map_manager.shoot_distance(azimuth, natomil)
            self.fastapi_send_coordinates(coordinates)

    def _resume_computation(self) -> None:
        self._pause.set()

    def _pause_computation(self) -> None:
        self._pause.clear()

    def _quit_computation_thread(self) -> None:
        self._running = False

    def _run_easyocr(self) -> None:
        """
        Runs the EasyOCR process by initiating and starting a separate process.
        
        It passes the class attributes `azimuth` and `natomil` as arguments to the function. The method
        ensures the EasyOCR parsing begins as a subprocess to allow for asynchronous
        execution.
        """
        print("Creating EasyOCR Process")
        self.process_parser = Process(target=screenparser.parse_my_screen, args=(self.azimuth, self.natomil))
        self.process_parser.start()
        print("Started EasyOCR Process")

    def stop_threads_and_tasks(self) -> None:
        if self.process_parser and self.process_parser.is_alive():
            self.process_parser.terminate()
            self.process_parser.join()
            self.process_parser.close()
            print("EasyOCR process terminated.")
        else:
            raise RuntimeError(
                "Cannot terminate: No process is currently running or the process has already been terminated.")

        if self.thread_mortar and self.thread_mortar.is_alive():
            self.thread_mortar.join()
            print("thread_mortar terminated")
        if self.thread_computation and self.thread_computation.is_alive():
            self._quit_computation_thread()
            self.thread_computation.join()
            print("thread_computation terminated")



    def fastapi_send_coordinates(self, coordinates: tuple[int, int]) -> None:
        self.fastapi_reference.change_xy(coordinates)

    def fastapi_pause(self):
        self.fastapi_reference.pause_sending_coordinates()

    def fastapi_resume(self):
        self.fastapi_reference.resume_sending_coordinates()
