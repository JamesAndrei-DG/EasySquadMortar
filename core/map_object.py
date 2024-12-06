import re
from PySide6.QtCore import QObject, Slot, Signal
from core.parse_maps import parsemaps


class Maps(QObject):

    def __init__(self):
        QObject.__init__(self)
        self.map_names = []

    def get_map_name(self):
        map_data = parsemaps()

        for i, data in enumerate(map_data):
            self.map_names.append(data[0])
            self.map_names[i] = re.sub(r"(\w)([A-Z])", r"\1 \2", self.map_names[i])

        return self.map_names

    @Slot(str)
    def selected_map(self, message: str):
        print(f"Selected map is: {message}")

    @Slot(str)
    def mortar_position(self, location: str):
        print(f"Origin is: {location}")