import re
from PySide6.QtCore import QObject, Slot, Signal
from core.parse_maps import parsemaps
from core.map_functions import MapFunction
import threading


class Maps(QObject):
    keypad_received = Signal(str)

    def __init__(self):
        QObject.__init__(self)
        self.map_names = []
        self.target_keypad = ''

        self.map_data = parsemaps()
        self.MapFunction = MapFunction()

    def get_map_names(self):
        for i, data in enumerate(self.map_data):
            self.map_names.append(data[0])
            self.map_names[i] = re.sub(r"(\w)([A-Z])|_", r"\1 \2", self.map_names[i])

        return self.map_names

    @Slot(str)
    def selected_map(self, map_index: int):
        # Need a way to check for exceptions/errors
        # Might need to add this to a thread if it is still hang
        print(f"Selected map index: {map_index}")
        self.MapFunction.change_map(map_index)

    @Slot(str)
    def mortar_position(self, keypad: str):
        print(f"Origin is: {keypad}")
        # thread = threading.Thread(target=self.MapFunction.set_origin_keypad, args=(keypad,))
        # thread.start()

        self.MapFunction.set_origin_keypad(keypad)

    # For Testing
    @Slot(str)
    def target_position(self, keypad: str):
        # self.target_keypad = keypad
        # print(f"Target is: {keypad}")
        # value = self.MapFunction.shoot_distance(83,1470)
        # print("Location printing: I10-5-8-5-7")
        # test = self.MapFunction.get_keypad_position("I10-5-8-5-7")
        # print(f"{test}")

        # test2 = self.MapFunction.get_distance(1470* 0.981719 * 0.001,83)
        # print(f"Manual Fire \n{test2}")
        self.MapFunction.test_me()