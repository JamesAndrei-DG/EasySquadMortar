import re
from time import perf_counter
from PySide6.QtCore import QObject, Slot, Signal
from core.parse_maps import parse_maps
from core.map_functions import MapFunction
import threading


class Map(QObject):
    keypad_received = Signal(str)

    def __init__(self):
        super().__init__()
        self.map_names = []
        self.target_keypad = ''
        self.map_data = parse_maps()
        self.map_function = MapFunction()

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
            self.map_function.change_map(map_index)
        except Exception as error:  # Added exception handling
            print(f"Error encountered when selecting map: {error}")

    @Slot(str)
    def mortar_position(self, keypad: str):
        """
        Sets the mortar's origin using the given keypad.
        Executes the action in a new thread.
        """
        print(f"Origin is: {keypad}")
        threading.Thread(target=self.map_function.set_origin_keypad, args=(keypad,)).start()

    @Slot(str)
    def target_position(self, keypad: str):
        t1 = perf_counter()
        value = self.map_function.shoot_distance(82, 1473)
        t2 = perf_counter()
        time = (t2 - t1) * 1000
        print(f"Calculation Finished in {time} ms for precalculated")
        print(f"value is\n {value} meters")

        t1 = perf_counter()
        self.map_function.precalculated = False
        value = self.map_function.shoot_distance(82, 1473)
        t2 = perf_counter()
        time = (t2 - t1) * 1000
        print(f"Calculation Finished in {time} ms for approximation")
        print(f"value is\n {value} meters")



        # print(value)
        # print("Location printing: I10-5-8-5-7")
        # test = self.MapFunction.get_keypad_position("I10-5-8-5-7")
        # print(f"{test}")

        # test2 = self.MapFunction.get_distance(1470* 0.981719 * 0.001,83)
        # print(f"Manual Fire \n{test2}")
        # self.MapFunction.test_me()
