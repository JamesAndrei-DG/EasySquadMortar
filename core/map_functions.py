import math
import numpy as np
from scipy.interpolate import LinearNDInterpolator
from time import perf_counter

AZIMUTH_RANGE = 359
GRID_SIZE = 300


class MapFunction:
    def __init__(self):
        self.map_data = np.load("core/arrays/map_arrays_compressed.npz")
        self.current_map = self.map_data["array_0"]  # Default to Al Basrah
        self.precalculated_firing_solution = []
        self.origin_x = 0
        self.origin_y = 0
        self.precalculated = False

    def change_map(self, map_index: int) -> None:
        print("Changing current map")
        self.current_map = self.map_data[f"array_{map_index}"]

    def set_origin_xy(self, x: int, y: int) -> None:
        print(f"Setting origin to ({x}, {y})")
        self.origin_x = x
        self.origin_y = y
        self._precalculate_firing_solution()

    def set_origin_keypad(self, keypad: str) -> None:
        print(f"Setting origin using keypad: {keypad}")
        self.origin_x, self.origin_y = self.get_keypad_position(keypad)
        print(f"Calculated origin: x={self.origin_x}, y={self.origin_y}")
        self._precalculate_firing_solution()

    def get_keypad_position(self, keypad: str) -> tuple[int, int]:
        try:
            keys = keypad.split("-")
            x, y = self._calculate_initial_position(keys[0])
            for i, data in enumerate(keys[1:], start=1):
                x, y = self._update_position_with_key(data, x, y, i)
            interval = GRID_SIZE / 3 ** (len(keys) - 1)
            x += interval / 2
            y += interval / 2
            return int(x), int(y)
        except Exception as error:
            print(f"Error in get_keypad_position: {error}")
            raise

    def get_height(self, x: int, y: int) -> float:
        try:
            return self.current_map[x][y]
        except IndexError:
            print(f"Coordinates out of bounds: x={x}, y={y}")
            return 0
        except Exception as error:
            raise Exception(f"Error in get_height: {error}")

    def get_distance(self, rad: float, elevation_array: list[tuple[float, int, int]]) -> tuple[float, int, int]:
        origin_elevation = self.get_height(self.origin_x, self.origin_y)
        time = max(14, 21 - int((rad - 0.82) / 0.08))
        velocity = 110
        vx, vy = velocity * math.cos(rad), velocity * math.sin(rad)
        step = 0.01

        try:
            while True:
                time += step
                distance = vx * time
                elevation = origin_elevation + vy * time - 0.5 * 9.81 * time ** 2
                find_d = round(distance / 10)
                if elevation <= elevation_array[find_d][0]:
                    x_pos, y_pos = elevation_array[find_d][1:]
                    return distance, x_pos, y_pos
        except Exception as error:
            print(f"Error in get_distance: {error}")
            raise

    def _calculate_initial_position(self, key: str) -> tuple[int, int]:
        letter_value = ord(key[0].upper()) - 65
        keypad_number = int(key[1:]) - 1
        x = GRID_SIZE * letter_value
        y = GRID_SIZE * keypad_number
        return x, y

    def _update_position_with_key(self, key: str, x: int, y: int, depth: int) -> tuple[int, int]:
        data = int(key)
        x_offset = (data - 1) % 3
        y_offset = 2 - ((data - 1) // 3)
        interval = GRID_SIZE / 3 ** depth
        x += x_offset * interval
        y += y_offset * interval
        return x, y

    def _precalculate_firing_solution(self) -> None:
        self.precalculated = False
        print("Precalculating firing solution...")
        t1 = perf_counter()
        for azimuth in range(AZIMUTH_RANGE):
            distances = self._calculate_all_possible_distances_from_azimuth(azimuth)
            self.precalculated_firing_solution.append(distances)
        t2 = perf_counter()
        print(f"Precalculation finished in {(t2 - t1) * 1000:.2f} ms")
        self.precalculated = True

    def _calculate_all_possible_distances_from_azimuth(self, azimuth: int) -> list[tuple[float, int, int]]:
        elevation_range = self._calculate_elevation_range_from_azimuth(azimuth)
        return [
            self.get_distance(natomil * 0.981719 * 0.001, elevation_range)
            for natomil in range(800, 1581, 10)
        ]
