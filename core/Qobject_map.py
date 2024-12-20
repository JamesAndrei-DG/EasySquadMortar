import ctypes
import re
from multiprocessing import Value, Process
from threading import Thread
from time import perf_counter
from typing import Any

from PySide6.QtCore import QObject, Slot, Signal
import core.parse_screen as screenparser
from core.map_functions import MapFunction
from core.parse_maps import parse_maps
from core.Qobject_fastapi import ObjectFastApi


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
        self._pause = Value(ctypes.c_bool)  # To be implemented
        self._running = True
        self.thread = None
        self.parser_process = None
        self.fastapi_reference = fastapi

    def get_map_names(self):
        """
        Parses and formats the map names from the loaded map data.
        """
        for i, data in enumerate(self.map_data):
            self.map_names.append(data[0])
            self.map_names[i] = re.sub(r"(\w)([A-Z])|_", r"\1 \2", self.map_names[i])

        return self.map_names

    @Slot(int)  # Fixed the type annotation for map_index
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
        self.thread = Thread(target=self.map_manager.set_origin_keypad, args=(keypad,))
        self.thread.start()

        # self.run_computation()

    def run_computation(self) -> None:
        x = 0
        y = 0
        while True:
            import time
            self.fastapi_send_coordinates(x, y)
            x += 1
            y += 1
            time.sleep(1)

    def _get_azimuth_natomils(self) -> None:
        pass

    def fastapi_send_coordinates(self, x: int, y: int) -> None:
        self.fastapi_reference.change_xy(x, y)

    def fastapi_pause(self):
        self.fastapi_reference.pause_sending_coordinates()

    def fastapi_resume(self):
        self.fastapi_reference.resume_sending_coordinates()

    @Slot(str)
    def target_position(self, keypad: str):
        t1 = perf_counter()
        value = self.map_manager.shoot_distance(82, 1473)
        t2 = perf_counter()
        time = (t2 - t1) * 1000
        print(f"Calculation Finished in {time} ms for precalculated")
        print(f"value is\n {value} meters")

        t1 = perf_counter()
        self.map_manager.precalculated = False
        value = self.map_manager.shoot_distance(82, 1473)
        t2 = perf_counter()
        time = (t2 - t1) * 1000
        print(f"Calculation Finished in {time} ms for approximation")
        print(f"value is\n {value} meters")

    def run_easyocr(self) -> None:
        """
        Runs the EasyOCR process by initiating and starting a separate process.
        
        It passes the class attributes `azimuth` and `natomil` as arguments to the function. The method
        ensures the EasyOCR parsing begins as a subprocess to allow for asynchronous
        execution.
        """
        self.parser_process = Process(target=screenparser.parse_my_screen, args=(self.azimuth, self.natomil))
        self.parser_process.start()

    def terminate_easyocr(self) -> None:
        if self.parser_process and self.parser_process.is_alive():
            self.parser_process.terminate()
            self.parser_process.join()
            self.parser_process.close()
            print("EasyOCR process terminated.")
        else:
            raise RuntimeError(
                "Cannot terminate: No process is currently running or the process has already been terminated.")
