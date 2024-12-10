import math
import numpy as np
import numpy.typing as npt
from time import perf_counter
import inspect


class MapFunction:
    def __init__(self):
        # Initialize map array and set to first array(Al Basrah)
        self.maps_arrays = np.load("core/arrays/map_arrays_compressed.npz")
        self.array_map_height = self.maps_arrays["array_0"]  # Map default is al basrah

        # Initialize heightline
        self.array_heightlines = []

        self.origin_x = 0
        self.origin_y = 0

        # bool
        self.precalculated = False

    def change_map(self, array_number: int) -> None:
        print(f"Changing array map")
        self.array_map_height = self.maps_arrays[f"array_{array_number}"]

    def set_origin_xy(self, x: int, y: int) -> None:  # return true
        print(f"Setting Origin ({x},{y})")
        self.origin_x = x
        self.origin_y = y
        self._precalculate_fire_solution()

    def set_origin_keypad(self, keypad: str) -> None:
        print(f"Setting Origin to keypad: {keypad}")
        self.origin_x, self.origin_y = self.get_keypad_position(keypad)
        print(f"x: {self.origin_x} y: {self.origin_y}")
        self._precalculate_fire_solution()

    # Need to sanitize before using function
    def get_keypad_position(self, keypad: str) -> tuple:
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
            print(f"Error Encountered in {inspect.currentframe().f_code.co_name}\n{error}")

    def xy_to_keypad(self):
        pass

    def get_height(self, x: int, y: int) -> float:
        # is there better way to fix this?
        # if x > 0 or y > 0 :
        #     raise ValueError(f"x:{x} y:{y} is invalid")
        # elif x > size or y > size:
        #     raise ValueError(f"x:{x} y:{y} is invalid")
        try:
            return self.array_map_height[x][y]
        except IndexError:
            print(f"x:{x} y:{y} is out of bounds")
            return 0
        except Exception as error:
            raise Exception(f"Error Encountered in {inspect.currentframe().f_code.co_name}\n{error}")

    def get_distance(self, rad: float, elevation_array: list) -> int:
        origin_elevation = self.get_height(self.origin_x, self.origin_y)
        x = 0
        y = 0
        if rad > 1.36:
            t = 21
        elif rad > 1.22:
            t = 20
        elif rad > 1.11:
            t = 19
        elif rad > 1.03:
            t = 18
        elif rad > 0.95:
            t = 17
        elif rad > 0.87:
            t = 16
        elif rad > 0.82:
            t = 15
        else:
            t = 14
        velocity = 110
        vx = velocity * math.cos(rad)
        vy = velocity * math.sin(rad)
        step = 0.01
        height_arr = elevation_array
        try:
            while True:
                # Update position
                t += step
                x = vx * t
                y = origin_elevation + vy * t - 0.5 * 9.81 * t ** 2

                find_x = round(x / 10)

                if y <= height_arr[find_x]:
                    # print(f"distance: {x}meters in {t} steps with rad: {rad} deg{np.rad2deg(rad)}")
                    return x  # Impact point

                # Increment time
                t += step
        except Exception as error:
            print(f"Error Encountered in {inspect.currentframe().f_code.co_name}\n{error}")

    def _calculate_all_possible_distances_from_azimuth(self, azimuth: int) -> list:
        result = []
        elevation_range = self._calculate_elevation_range_from_azimuth(azimuth)
        for natomil in range(800, 1580 + 1, 10):
            result.append(self.get_distance((natomil * 0.981719 * 0.001), elevation_range))  # natomil to rad

        return result

    def _calculate_elevation_range_from_azimuth(self, azimuth: int) -> list:
        rad = azimuth * math.pi / 180
        # find height 0-1500 meters out with 10 meters step lets check later if i can make it more resolution
        x_scale = np.sin(rad)
        y_scale = np.cos(rad)
        height_array = []

        for meters in range(0, 1500, 10):
            x_find = self.origin_x + int(meters * x_scale)
            y_find = self.origin_y - int(meters * y_scale)  # Needs to be inverted
            height_array.append(self.get_height(int(x_find), int(y_find)))

        return height_array

    def _precalculate_fire_solution(self) -> None:
        self.precalculated = False
        print("Precalculating fire solution")
        t1 = perf_counter()
        for azimuth in range(359):
            self.array_heightlines.append(self._calculate_all_possible_distances_from_azimuth(azimuth))
        t2 = perf_counter()
        time = (t2 - t1) * 1000
        print(f"Calculation Finished in {time} ms")
        self.precalculated = True

    def shoot_distance(self, bearing: float, natomils: int) -> int:
        # Check Exceptions
        if natomils < 800 or natomils > 1580:
            raise ValueError(f"{natomils} is an invalid input in natomils")
        elif bearing < 0 or bearing > 359:
            raise ValueError(f"{bearing} is an invalid input in bearing")

        # If not precalculated
        if self.precalculated == False:
            # approximation
            elevation_array = self._calculate_elevation_range_from_azimuth(int(bearing))
            return self.get_distance(natomils * 0.981719 * 0.001, elevation_array)


        index = max(0, int((natomils - 800) / 10))
        true_natomils = float(natomils/10)
        true_bearing = bearing


        try:
            value = self.array_heightlines[int(bearing)][index]
            print("Shoot success")
            print(value)
            return value
        except Exception as error:
            print(f"Error Encountered in {inspect.currentframe().f_code.co_name}\n{error}")

    def test_me(self):
        print("testing")
        array = self._calculate_elevation_range_from_azimuth(83)
        print("target height at 300m")
        value = array[30]
        print(value)

        print(f"height at x")
        x, y = self.get_keypad_position("I10-5-8-5-7")
        print(f"x :{x} y:{y}")
        print(self.get_height(x, y))

        print(f"\nShooting")
        self.shoot_distance(83, 1470)
