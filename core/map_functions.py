import math
import numpy as np
from time import perf_counter


class MapFunction:
    def __init__(self):
        # Initialize map array and set to first array(Al Basrah)
        self.maps_arrays = np.load("core/arrays/map_arrays_compressed.npz")
        self.array_map_height = self.maps_arrays["array_0"]  # Map default is al basrah

        # Initialize heightline
        self.array_heightlines = []

        self.origin_x = 0
        self.origin_y = 0  # should be zero

    def change_map(self, array_number):
        print(f"Changing array map")
        self.array_map_height = self.maps_arrays[f"array_{array_number}"]

    def set_origin_xy(self, x, y):
        print(f"Setting Origin ({x},{y})")
        self.origin_x = x
        self.origin_y = y
        self._precalculate_fire_solution()

    def set_origin_keypad(self, keypad):
        print(f"Setting Origin to keypad: {keypad}")
        self.origin_x, self.origin_y = self.get_keypad_position(keypad)
        print(f"x: {self.origin_x} y: {self.origin_y}")
        self._precalculate_fire_solution()

    # Need to sanitize before using get_position
    def get_keypad_position(self, keypad):
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
            print(f"Error Encountered in get_keypad_position\n{error}")

    def get_height(self, x, y):
        return self.array_map_height[x][y]

    def get_distance(self, rad, height_array):
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
        height_arr = height_array
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
            print(f"Error Encountered in get_distance\n{error}")

    def get_height_range_from_azimuth(self, azimuth):
        result = []
        height_array = self._get_height_line_array(azimuth)
        for natomil in range(800, 1580 + 1, 10):
            result.append(self.get_distance((natomil * 0.981719 * 0.001), height_array))

        return result

    def _get_height_line_array(self, azimuth):
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

    def _precalculate_fire_solution(self):
        print("Precalculating fire solution")
        t1 = perf_counter()
        for azimuth in range(359):
            self.array_heightlines.append(self.get_height_range_from_azimuth(azimuth))
        t2 = perf_counter()
        time = (t2 - t1) * 1000
        print(f"Calculation Finished in {time} ms")

    def shoot_distance(self, azimuth, natomils):
        if natomils < 800 or natomils > 1580:
            raise ValueError(f"{natomils} is an invalid input in natomils")
        elif azimuth < 0 or azimuth > 359:
            raise ValueError(f"{azimuth} is an invalid input in azimuth")

        index = int((natomils - 800) / 10)
        try:
            value = self.array_heightlines[azimuth][index]
            print("Shoot success")
            print(value)
            return value
        except Exception as error:
            print(f"Error Encountered in shoot_distance\n{error}")

    def test_me(self):
        print("testing")
        array = self._get_height_line_array(83)
        print("target height at 300m")
        value = array[30]
        print(value)

        print(f"height at x")
        x, y = self.get_keypad_position("I10-5-8-5-7")
        print(f"x :{x} y:{y}")
        print(self.get_height(x, y))

        print(f"\nShooting")
        self.shoot_distance(83, 1470)
