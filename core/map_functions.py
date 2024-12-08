import math
import numpy as np





class MapFunction:
    def __init__(self, size):
        # Initialize map array and set to first array(Al Basrah)
        self.array_maps = np.load("core/arrays/map_arrays_compressed.npz")
        self.array_height = np.zeros((int(size), int(size)), dtype=np.float16)
        self.array_height = self.array_maps["array_0"]

        # Initialize heightline
        self.array_heightlines = []

        self.origin_x = 0
        self.origin_y = 0  # should be zero

        # do calculations remove before production

    def change_map(self, array_number):
        self.array_height = self.array_maps[f"array_{array_number}"]

    def set_origin(self, x, y):
        self.origin_x = x
        self.origin_y = y
        self._precalculate_fire_solution()

    # Need to sanitize before using get_position
    def get_keypad_position(self, keypad):
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

    def get_height(self, x, y):
        return self.array_height[x][y]

    def get_distance(self, rad, azimuth):
        origin_elevation = self.get_height(self.origin_x, self.origin_y)
        x = 0
        y = 0
        t = 14
        velocity = 110
        vx = velocity * math.cos(rad)
        vy = velocity * math.sin(rad)
        step = 1
        height = self._get_height_line_array(azimuth)

        while True:
            # Update position
            t += step
            x = vx * t
            y = origin_elevation + vy * t - 0.5 * 9.81 * t ** 2

            find_x = round(x / 10)
            height_at_x = height[find_x]

            # Check for impact
            if y <= height_at_x:
                # print(f"distance: {x}meters in {t} steps")
                return x  # Impact point

            # Increment time
            t += step

    def get_height_range_from_azimuth(self, az):
        result = []

        for natomil in range(800, 1580 + 1, 10):
            result.append(self.get_distance((natomil * 0.981719 * 0.001), az))

        # test
        if az == 354:
            print("double checking")

        return result

    def _get_height_line_array(self, azimuth):
        rad = azimuth * math.pi / 180
        # find height 0-1500 meters out with 10 meters step lets check later if i can make it more resolution
        x_scale = np.sin(rad)
        y_scale = np.cos(rad)
        height_array = []

        for meters in range(0, 1500, 10):
            x_find = self.origin_x + meters * x_scale
            y_find = self.origin_y + meters * y_scale
            height_array.append(self.get_height(int(x_find), int(y_find)))
            # height_array.append(self.get_height(x_find,y_find))
        # print(f"Azimuth: {azimuth}")
        # print(height_array)
        return height_array


    def _precalculate_fire_solution(self):
        print("Precalculating fire solution")
        for azimuth in range(359):
            self.array_heightlines.append(self.get_height_range_from_azimuth(azimuth))
