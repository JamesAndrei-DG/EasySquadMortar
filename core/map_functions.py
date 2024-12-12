import math
import numpy as np
from scipy.interpolate import LinearNDInterpolator
from time import perf_counter
import inspect

import scipy.interpolate


class MapFunction:
    def __init__(self):
        # Initialize map array and set to first array(Al Basrah)
        self.maps_arrays = np.load("core/arrays/map_arrays_compressed.npz")
        self.array_map_height = self.maps_arrays["array_0"]  # Map default is al basrah

        # Contents:
        # precalculated_firing_solution[azimuth][NATOmil/step][0] height #step should be 10
        # precalculated_firing solution[azimuth][NATOmil/step][1] x_location
        # precalculated_firing solution[azimuth][NATOmil/step][1] y_location
        self.precalculated_firing_solution = []  # list of list of tuples

        self.origin_x = 0
        self.origin_y = 0

        # bool
        self.precalculated = False

    def change_map(self, array_number: int) -> None:
        print(f"Changing array map")
        self.array_map_height = self.maps_arrays[f"array_{array_number}"]

    def set_origin_xy(self, x: int, y: int) -> None:  # return true
        print(f"Setting Origin ({x},{y})")  # check if out of bounds
        self.origin_x = x
        self.origin_y = y
        self._precalculate_fire_solution()

    def set_origin_keypad(self, keypad: str) -> None:
        print(f"Setting Origin to keypad: {keypad}")
        self.origin_x, self.origin_y = self.get_keypad_position(keypad)
        print(f"x: {self.origin_x} y: {self.origin_y}")
        self._precalculate_fire_solution()

    # Need to sanitize before using function
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
        height_arr = elevation_array
        try:
            while True:
                # Update position
                time += step
                distance = vx * time
                elevation = origin_elevation + vy * time - 0.5 * 9.81 * time ** 2

                find_d = round(distance / 10)  # it will cause error if it is negative

                if elevation <= height_arr[find_d][0]:
                    # print(f"distance: {x}meters in {t} steps with rad: {rad} deg{np.rad2deg(rad)}")
                    x_pos = height_arr[find_d][1]
                    y_pos = height_arr[find_d][2]
                    return distance, x_pos, y_pos  # Impact point and position

                # Increment time
                time += step
        except Exception as error:
            print(f"Error Encountered in {inspect.currentframe().f_code.co_name}\n{error}")

    def _calculate_all_possible_distances_from_azimuth(self, azimuth: int) -> list[tuple[float, int, int]]:
        result = []
        elevation_range = self._calculate_elevation_range_from_azimuth(azimuth)
        for natomil in range(800, 1580 + 1, 10):
            result.append(self.get_distance((natomil * 0.981719 * 0.001), elevation_range))  # natomil to rad

        return result

    def _find_xy_from_origin(self, azimuth_f: float, distance: float) -> tuple[int, int]:
        rad = azimuth_f * math.pi / 180
        x_scale = np.sin(rad)
        y_scale = np.cos(rad)
        x_find = int(self.origin_x + distance * x_scale)
        y_find = int(self.origin_x - distance * y_scale)
        return x_find, y_find

    def _calculate_elevation_range_from_azimuth(self, azimuth_f: float) -> list[tuple[float, int, int]]:
        rad = azimuth_f * math.pi / 180
        # find height 0-1500 meters out with 10 meters step lets check later if i can make it more resolution
        x_scale = np.sin(rad)
        y_scale = np.cos(rad)
        height_array = []

        for meters in range(0, 1500, 10):
            x_find = int(self.origin_x + meters * x_scale)
            y_find = int(self.origin_y - meters * y_scale)  # Needs to be inverted
            height_array.append((self.get_height(x_find, y_find), x_find, y_find))

        return height_array

    def _precalculate_fire_solution(self) -> None:
        self.precalculated = False
        print("Precalculating fire solution")
        t1 = perf_counter()
        for azimuth in range(359):
            self.precalculated_firing_solution.append(self._calculate_all_possible_distances_from_azimuth(azimuth))
        t2 = perf_counter()
        time = (t2 - t1) * 1000
        print(f"Calculation Finished in {time} ms")
        self.precalculated = True

    def _interpolate_from_4points(self, points: list[tuple[int, int]], distances: list[float], azimuth_f: float,
                                  natomils: int) -> float:
        try:
            _f = LinearNDInterpolator(points, distances)
            distancebearing = _f(azimuth_f, natomils)
            # print(f"distance is {distancebearing}")
            return distancebearing
        except Exception as error:
            print(f"Error Encountered in {inspect.currentframe().f_code.co_name}\n{error}")

    def shoot_distance(self, azimuth_f: float, natomils: int) -> tuple[int, int]:
        # Check Exceptions
        if natomils < 800 or natomils > 1580:
            raise ValueError(f"{natomils} is an invalid input in natomils")
        elif azimuth_f < 0 or azimuth_f > 359:
            raise ValueError(f"{azimuth_f} is an invalid input in azimuth")

        # If not precalculated
        if not self.precalculated:
            # approximate
            # print(f"Pre-calculation not done doing approximation")
            elevation_array = self._calculate_elevation_range_from_azimuth(azimuth_f)
            distance, x , y = self.get_distance(natomils * 0.981719 * 0.001, elevation_array)

            return x, y

        i1 = max(0, int((natomils - 800) / 10))
        i2 = i1 + 1
        az1 = int(azimuth_f)
        az2 = int(azimuth_f + 1)

        points = [(az1, i1 * 10), (az1, i2 * 10), (az2, i1 * 10), (az2, i2 * 10)]

        try:
            # print(f"points\n {points}")
            # print(f"value for precalculated az1 i1 {self.precalculated_firing_solution[az1][i1][0]}")
            # print(f"value for precalculated az1 i2 {self.precalculated_firing_solution[az1][i2][0]}")
            # print(f"value for precalculated az2 i1 {self.precalculated_firing_solution[az2][i1][0]}")
            # print(f"value for precalculated az2 i2 {self.precalculated_firing_solution[az2][i2][0]}")

            distances = [self.precalculated_firing_solution[az1][i1][0], self.precalculated_firing_solution[az1][i2][0],
                         self.precalculated_firing_solution[az2][i1][0], self.precalculated_firing_solution[az2][i2][0]]

            meters = self._interpolate_from_4points(points, distances, azimuth_f, natomils-800)
            x, y = self._find_xy_from_origin(azimuth_f, meters)
            # print(f"x{x}y{y}")
            return x, y

        except Exception as error:
            print(f"Error Encountered in {inspect.currentframe().f_code.co_name}\n{error}")

    def test_me(self):
        print(f"height at x")
        x, y = self.get_keypad_position("I10-5-8-5-7")
        print(f"x :{x} y:{y}")
        print(self.get_height(x, y))

        print(f"\nShooting")
        self.shoot_distance(83, 1470)
