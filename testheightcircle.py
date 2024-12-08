import os
import sys
from os import cpu_count

import cv2
import time
import tracemalloc
import math
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot

from functools import wraps

from multiprocessing import Pool, Manager, Lock

def count_calls(args):
    func, lock, shared_counter, name = args

    with lock:  # Acquire lock to safely update the counter
        shared_counter.value += 1
        # print(f"{func.__name__} has been called {shared_counter.value} times.")

    return func(name)


def timer_and_memory(func):
    """
    A decorator to measure the execution time and memory usage of a function.
    """

    def wrapper(*args, **kwargs):
        # Start tracing memory
        tracemalloc.start()

        # Record start time with high precision
        start_time = time.perf_counter()

        # Execute the function
        result = func(*args, **kwargs)

        # Record end time
        end_time = time.perf_counter()

        # Capture memory usage
        current, peak = tracemalloc.get_traced_memory()

        # Stop tracing memory
        tracemalloc.stop()

        # Calculate elapsed time
        elapsed_time = end_time - start_time

        # Determine the appropriate time unit and format
        if elapsed_time >= 1:
            time_display = f"{elapsed_time:.10f} seconds"
        elif elapsed_time >= 0.001:  # Between 1 millisecond and 1 second
            time_display = f"{elapsed_time * 1000:.3f} milliseconds"
        else:  # Less than 1 millisecond
            time_display = f"{elapsed_time * 1_000_000:.3f} microseconds"

        # Display results
        print(f"Function '{func.__name__}' executed in {time_display}.")
        print(f"Current memory usage: {current / 1024:.2f} KB")
        print(f"Peak memory usage: {peak / 1024:.2f} KB")

        return result

    return wrapper


class Heightmap:
    def __init__(self, image_path):
        # Load the image
        self.image = cv2.imread(image_path, cv2.IMREAD_COLOR)

        self.scaling_xysizeratio = 1024 / 4617
        self.scaling_height = 0.733125
        self.height, self.width, _ = self.image.shape
        # print(f"height: {self.height}\nwidth: {self.width}")
        self.origin_x = 2500
        self.origin_y = 2500
        self.array_height = np.zeros((4617, 4617))
        self.load = np.load("core/arrays/map_arrays_compressed.npz")
        self.array_height = self.load["array_12"]
        self.t_calc = 0
        self.t_get_height = 0


    def get_height(self, find_x, find_y):
        # Adjust coordinates based on scaling
        scaled_x = round(find_x * self.scaling_xysizeratio)
        scaled_y = round(find_y * self.scaling_xysizeratio)  # origin_y-axis inversion
        # print(f"scaled_x: {scaled_x}\nscaled_y: {scaled_y}")

        # Check if coordinates are out of bounds
        if not (0 <= scaled_x < self.width and 0 <= scaled_y < self.height):
            return 0  # Out of map

        # Get pixel color (B, G, R)
        color = self.image[scaled_y, scaled_x]

        # print(f"color G: {color[1]}\ncolor R: {color[2]}\ncolor B: {color[0]} \nscaling height: {self.scaling_height}")
        # Calculate height
        if color[2] + color[0] <= 10:  # black does not show as all 0
            return 0  # Out of map
        else:
            height = ((255 + color[2] - color[0]) * self.scaling_height)
            # print(f"height : {height}")
            return height

    def show_point(self):
        # Clone the image to overlay markers
        display_image = self.image.copy()
        # Extract the height and scaled coordinates
        height, (scaled_x, scaled_y) = self.get_height(self.origin_x, self.origin_y)

        # Convert to BGR (OpenCV display format)
        display_image = cv2.cvtColor(display_image, cv2.COLOR_BGRA2BGR)

        # Draw the point on the image
        if 0 <= scaled_x < self.width and 0 <= abs(scaled_y) < self.height:
            cv2.circle(display_image, (scaled_x, scaled_y), 5, (0, 0, 255), -1)  # Red dot for point
            text = f"Height: {height:.2f}"
        else:
            text = "Point out of bounds"

        # Add text to the image
        cv2.putText(display_image, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # Display the image
        cv2.imshow("Heightmap", display_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def get_position(self, keypad):
        keys = keypad.split("-")

        for i, data in enumerate(keys):
            if i == 0:
                # Only works if it does not exceed letter z
                lettertonumber = ord(data[0]) - 65
                keypadnumber = int(data[1:3]) - 1

                self.origin_x = 300 * int(lettertonumber)
                self.origin_y = 300 * int(keypadnumber)

            else:
                data = int(data)
                x_between = (data - 1) % 3
                y_between = 2 - ((data - 1) // 3)
                interval = 300 / 3 ** i

                self.origin_x += x_between * interval
                self.origin_y += y_between * interval

        interval = 300 / 3 ** (len(keys) - 1)
        self.origin_x += interval / 2
        self.origin_y += interval / 2
        self.origin_x = int(self.origin_x)
        self.origin_y = int(self.origin_y)

        # print(f"x: {self.origin_x}\ny: {self.origin_y}")


    def get_height_line_array(self, azimuth):
        rad = azimuth * math.pi / 180
        # print(f"azimuth: {azimuth}\nrad: {rad}")
        # find height 0-1500 meters out with 10 meters step lets check later if i can make it more resolution
        x_scale = np.sin(rad)
        y_scale = np.cos(rad)
        height_array = []

        for meters in range(0, 1500, 10):
            x_find = self.origin_x + meters * x_scale
            y_find = self.origin_y + meters * y_scale
            height_array.append(self.find_from_array(int(x_find), int(y_find)))
            # height_array.append(self.get_height(x_find,y_find))
        # print(f"Azimuth: {azimuth}")
        # print(height_array)
        return height_array

    def get_height_array(self):
        # for changing y
        y = self.origin_y
        x = self.origin_x
        points = 0
        i = 0
        height_array = self.get_height_line_array(0)

        for value in range(x, (x + 360)):
            j = 0
            self.array_height[i] = i
            for value2 in range(y, (y - 1500), -10):

                self.array_height[i][j] = self.get_height(value, value2)
                if i == 350 and j == 140:
                    print(f"height @ \nazimuth: {i}\ndistance: {j}\nheight: {self.get_height(value, value2)}")

                points += 1
                j += 1
            i += 1

        # print(f"{self.array_height[350][140]}")

    def load_array(self):
        self.array_height = np.load('assets/kohat/heightmap_array.npy')

    def find_from_array(self, x, y):
        return self.array_height[x][y]

    def get_distance(self, rad, azimuth, heightline):
        origin_elevation = self.find_from_array(self.origin_x, self.origin_y)
        x = 0
        y = origin_elevation
        if rad >= 1.36:
            t = 22
        elif rad >= 1.17:
            t = 20
        elif rad >= 0.92:
            t = 18
        else:
            t = 14
        velocity = 110
        vx = velocity * math.cos(rad)
        vy = velocity * math.sin(rad)
        step = 1
        degree = rad * 180 / math.pi


        while True:
            # Update position
            t += step
            x = vx * t
            y = origin_elevation + vy * t - 0.5 * 9.81 * t ** 2

            find_x = round(x / 10)
            self.t_calc += 1

            # Check for impact
            if y <= heightline[find_x]:
                # print(f"distance: {int(x)}meters in {t} steps @ degree: {degree} rad: {rad}")

                return x  # Impact point

            # Increment time
            t += step

    def get_height_range(self, azimuth_range):
        result = []
        for each in azimuth_range:
            for natomil in range(800, 1580, 10):
                result.append(self.get_distance((natomil * 0.981719 * 0.001), each))

        return result


    def get_height_range_az(self, az):
        result = []
        heightline = self.get_height_line_array(az)

        for natomil in range(800, 1580, 10):

            result.append(self.get_distance((natomil * 0.981719 * 0.001), az, heightline))

        return result

    def calculate_the_circle(self):
        with Manager() as manager:
            shared_counter = manager.Value('i', 0)  # Shared integer initialized to 0
            lock = manager.Lock()


            # Use a Pool to parallelize calls
            with Pool(processes=1) as pool:
                # Prepare arguments: func, lock, shared_counter, and name
                args = [(self.get_height_range_az, lock, shared_counter, i)for i in range(359)]

                # Execute the pool function
                results = pool.map(count_calls, args)

            print(f"greet was called {shared_counter.value} times.")
            print(f"cpucount{cpu_count()}")




        # # use multi proces to calculate the 360 for each azimuth
        # myrange = range(359)
        #
        # p = Pool()
        # result = p.map(self.get_height_range_az, myrange)
        # # print(result)

    def calc_me(self):
        result =[]
        for azimuth in range(359):
            result.append(self.get_height_range_az(azimuth))

    def test_get_height_range(self):
        result = []
        for natomil in range(800, 1580, 10):
            result.append(self.get_distance((natomil * 0.981719 * 0.001), 10))

    def test_get_distance_one(self):
        self.get_distance((800 * 0.981719 * 0.001), 10)

    def test_parabola_range(self):
        azimuth = 10
        y = self.get_height_line_array(azimuth)
        x = np.arange(len(y))

        params, covariance = curve_fit(self.quadratic_model, x, y)
        a, b, c = params

        height_function = self.quadratic_model(x, a, b, c)
        matplotlib.pyplot.scatter(x, y, label="original Data", color='blue')
        matplotlib.pyplot.plot(x, height_function, label='Fitted Curve', color='red')
        matplotlib.pyplot.legend()
        matplotlib.pyplot.xlabel('x')
        matplotlib.pyplot.ylabel('y')
        matplotlib.pyplot.title('Curve Fitting Example')
        matplotlib.pyplot.show()

    def quadratic_model(self, x, a, b, c):
        return a * x ** 2 + b * x + c


@timer_and_memory
def getheight():
    # Example usage
    heightmap = Heightmap("assets/kohat/heightmap.webp")
    # heightmap.load_array()
    # for azimuth in range(359):
    # for natomil in range(800,1580,10):
    # heightmap.get_distance((natomil * 0.981719 * 0.001),azimuth)

    all_height = []
    # for azimuth in range(359):
    #     test = heightmap.get_height_line_array(azimuth)
    #     all_height.append(test)

    # print(f"size of all_height: {sys.getsizeof(all_height)}")

    # for multiprocessor
    # heightmap.calculate_the_circle()
    heightmap.calc_me()

    # heightmap.test_get_distance_one()
    # heightmap.test_get_height_range()

    # heightmap.test_parabola_range()
    print(f"t calc = {heightmap.t_calc}")


if __name__ == '__main__':
    getheight()

