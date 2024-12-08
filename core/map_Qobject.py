import re
from PySide6.QtCore import QObject, Slot, Signal
from core.parse_maps import parsemaps
from core.map_functions import MapFunction


class Maps(QObject):
    keypad_received = Signal(str)

    def __init__(self):
        QObject.__init__(self)
        self.map_names = []
        self.target_keypad = ''

        self.map_data = parsemaps()
        self.MapFunction = MapFunction(self.map_data[0][1],) #initialize map function to first array


    def get_map_names(self):
        for i, data in enumerate(self.map_data):
            self.map_names.append(data[0])
            self.map_names[i] = re.sub(r"(\w)([A-Z])", r"\1 \2", self.map_names[i])

        return self.map_names

    @Slot(str)
    def selected_map(self, map: str):
        print(f"Selected map is: {map}")

    @Slot(str)
    def mortar_position(self, keypad: str):
        print(f"Origin is: {keypad}")

    # For Testing
    @Slot(str)
    def target_position(self, keypad: str):
        self.target_keypad = keypad
