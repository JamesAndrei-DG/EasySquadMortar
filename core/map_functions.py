import math
import numpy as np
from time import perf_counter
from scipy.interpolate import LinearNDInterpolator

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
            x = 0
            y = 0

            for i, data in enumerate(keys):
                if i == 0:
                    # Only works if it does not exceed letter z
                    lettertonumber = ord(data[0]) - 65
                    keypadnumber = int(data[1:3]) - 1

                    x = 300 * int(lettertonumber)
                    y = 300 * int(keypadnumber)

                else:
                    data = int(data)
                    x_between = (data - 1) % 3
                    y_between = 2 - ((data - 1) // 3)
                    interval = 300 / 3 ** i

                    x += x_between * interval
                    y += y_between * interval

            interval = 300 / 3 ** (len(keys) - 1)
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
        if rad > 1.36:
            time = 21
        elif rad > 1.22:
            time = 20
        elif rad > 1.11:
            time = 19
        elif rad > 1.03:
            time = 18
        elif rad > 0.95:
            time = 17
        elif rad > 0.87:
            time = 16
        elif rad > 0.82:
            time = 15
        else:
            time = 14
        velocity = 110
        vx = velocity * math.cos(rad)
        vy = velocity * math.sin(rad)
        step = 0.01

        try:
            while True:
                time += step
                distance = vx * time
                elevation = origin_elevation + vy * time - 0.5 * 9.81 * time ** 2
                find_d = round(distance / 10)  # it will cause error if it is negative
                if elevation <= elevation_array[find_d][0]:
                    x_pos, y_pos = elevation_array[find_d][1:]
                    return distance, x_pos, y_pos
        except Exception as error:
            print(f"Error in get_distance: {error}")
            raise

    def _precalculate_firing_solution(self) -> None:
        self.precalculated = False
        print("Precalculating firing solution")
        t1 = perf_counter()
        for azimuth in range(359):
            self.precalculated_firing_solution.append(self._calculate_all_possible_distances_from_azimuth(azimuth))
        t2 = perf_counter()
        time = (t2 - t1) * 1000
        print(f"Calculation Finished in {time} ms")
        self.precalculated = True

    def _calculate_all_possible_distances_from_azimuth(self, azimuth: int) -> list[tuple[float, int, int]]:
        result = []
        elevation_range = self._calculate_elevation_range_from_azimuth(azimuth)
        for natomil in range(800, 1580 + 1, 10):
            result.append(self.get_distance((natomil * 0.981719 * 0.001), elevation_range))
        return result

    def _calculate_elevation_range_from_azimuth(self, azimuth: int) -> list[tuple[float, int, int]]:
        rad = azimuth * math.pi / 180
        # find height 0-1500 meters out with 10 meters step lets check later if I can make it more resolution
        x_scale = np.sin(rad)
        y_scale = np.cos(rad)
        height_array = []

        for meters in range(0, 1500, 10):
            x_find = int(self.origin_x + meters * x_scale)
            y_find = int(self.origin_y - meters * y_scale)  # Needs to be inverted
            height_array.append((self.get_height(x_find, y_find), x_find, y_find))

        return height_array

    def _interpolate_from_4points(self, points: list[tuple[int, int]], distances: list[float], azimuth_f: float,
                                  natomils: int) -> float:
        _f = LinearNDInterpolator(points, distances)
        distancebearing = _f(azimuth_f, natomils)
        if distancebearing:
            return distancebearing
        else:
            raise ValueError(f"Natomils: {natomils} or Azimuth: {azimuth_f} out of bounds")

def shoot_distance(self, azimuth_f: float, natomils: int) -> tuple[int, int]:
    # Check Exceptions
    if natomils < 800 or natomils > 1580:
        raise ValueError(f"{natomils} is an invalid input in natomils")
    elif azimuth_f < 0 or azimuth_f > 359:
        raise ValueError(f"{azimuth_f} is an invalid input in azimuth")
    try:
        # If not precalculated
        if not self.precalculated:
            # approximate
            elevation_array = self._calculate_elevation_range_from_azimuth(azimuth_f)
            distance, x, y = self.get_distance(natomils * 0.981719 * 0.001, elevation_array)
            return x, y
        i1 = max(0, int((natomils - 800) / 10))
        i2 = i1 + 1
        az1 = int(azimuth_f)
        az2 = int(azimuth_f + 1)
        distance1 = (self.precalculated_firing_solution[az1][i1][0] + self.precalculated_firing_solution[az2][i1][
            0]) / 2
        distance2 = (self.precalculated_firing_solution[az1][i2][0] + self.precalculated_firing_solution[az2][i2][
            0]) / 2
        # Linear interpolation
        distance = distance1 + (distance2 - distance1) * (natomils % 10) / 10
        return self._find_xy_from_origin(azimuth_f, distance)
    except Exception as error:
        print(f"Error Encountered in shoot_distance\n{error}")

