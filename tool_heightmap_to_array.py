import cv2
import time
import tracemalloc
import numpy as np

from core.parse_maps import parsemaps

maps_array = parsemaps()


def timer_and_memory(func):
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

        # Display results with high precision
        print(f"Function '{func.__name__}' executed in {end_time - start_time:.10f} seconds.")
        print(f"Current memory usage: {current / 1024:.2f} KB")
        print(f"Peak memory usage: {peak / 1024:.2f} KB")

        return result

    return wrapper


class Heightmap:
    def __init__(self, directory, size, scaling):
        self.dir = directory
        # Load the image
        self.image = cv2.imread(str(directory + "heightmap.webp"), cv2.IMREAD_COLOR)
        self.height, self.width, _ = self.image.shape  # heightmap size

        self.scaling_xysizeratio = self.height / size  # heightmapsize / original size assuming map is square
        self.scaling_height = scaling  # based on map Scaling attribute

        # print(f"height: {self.height}\nwidth: {self.width}")
        self.array = np.zeros((int(size), int(size)), dtype=np.float16)  # array should be size of original map

        # buffer x and y
        self.buffer_x = 0
        self.buffer_y = 0
        self.buffer_height = 0

    def get_height(self, find_x, find_y):
        # Adjust coordinates based on scaling
        scaled_x = round(find_x * self.scaling_xysizeratio)
        scaled_y = round(find_y * self.scaling_xysizeratio)  # origin_y-axis inversion

        if not (0 <= scaled_x < self.width and 0 <= scaled_y < self.height):
            return 0

        if self.buffer_x == scaled_x and self.buffer_y == scaled_y:
            return self.buffer_height

        # Color (B, G, R)
        color = self.image[scaled_y, scaled_x]

        # Calculate height
        if int(color[2]) + int(color[0]) <= 10:  # black does not show as all 0
            self.buffer_x = scaled_x
            self.buffer_y = scaled_y
            self.buffer_height = 0
            return 0
        else:
            height = np.float16(float(255 - int(color[0]) + int(color[2])) * self.scaling_height)
            self.buffer_x = scaled_x
            self.buffer_y = scaled_y
            self.buffer_height = height
            return height

    def get_heightmap_to_array(self):
        for x in range(self.array.shape[0]):
            for y in range(self.array.shape[1]):
                self.array[x][y] = self.get_height(x, y)

    def save_array(self):
        np.save(str(self.dir + 'heightmap_array.npy'), self.array)

    def load_array(self):
        self.array = np.load(str(self.dir + 'heightmap_array.npy'))

    def get_height_from_array(self, x, y):
        height = self.array[x][y]
        # print(f"----array----\nheight @[{x}][{y}]: {self.array[x][y]}")

    def get_height_from_map(self, x, y):
        height = self.get_height(x, y)
        # print(f"----heightmap----\nheight @[{x}][{y}]: {height}")

    def get_max_array(self):
        return self.array.max(), self.array.argmax()

    def get_min_array(self):
        return self.array.min(), self.array.argmin()

    def get_array(self):
        return self.array


# @timer_and_memory
def for_heightmap(directory, size, scaling):
    heightmap = Heightmap("assets" + directory, size, scaling)
    for x in range(0, 1200, 2):
        for y in range(0, 1200, 2):
            heightmap.get_height_from_map((10 + x), (10 + y))


# @timer_and_memory
def for_array(directory, size, scaling):
    heightmap = Heightmap("assets" + directory, size, scaling)
    heightmap.load_array()
    for x in range(0, 1200, 2):
        for y in range(0, 1200, 2):
            heightmap.get_height_from_array((10 + x), (10 + y))

def save_me():
    list_array = []
    for i, data in enumerate(maps_array):  # This will take a few minutes. will be faster if we use multiprocessing
        directory = data[3]
        size = data[1]
        scaling = data[2]

        print(f"map: {data[0]}")

        heightmap = Heightmap("assets" + directory, size, scaling)
        heightmap.get_heightmap_to_array()
        heightmap.save_array()
        array = heightmap.get_array()
        list_array.append(array)

    with open("core/arrays/map_arrays_compressed.npz", "wb") as f:
        np.savez_compressed(f, **{f"array_{i}": arr for i, arr in enumerate(list_array)})


@timer_and_memory
def save_me_load_existing_array():
    list_array = []
    for i, data in enumerate(maps_array):
        directory = data[3]
        size = data[1]
        scaling = data[2]

        print(f"map: {data[0]}")

        heightmap = Heightmap("assets" + directory, size, scaling)
        # heightmap.get_heightmap_to_array()
        # heightmap.save_array()
        try:
            heightmap.load_array()
        except Exception as error:
            print(f"Error occured {error}")
            print(f"Check if file is still existing. If not use save_me() function.")
        array = heightmap.get_array()
        list_array.append(array)

    with open("core/arrays/map_arrays_compressed.npz", "wb") as f:
        np.savez_compressed(f, **{f"array_{i}": arr for i, arr in enumerate(list_array)})

@timer_and_memory
def test_me():
    loaded = np.load("core/arrays/map_arrays_compressed.npz")

    for i, data in enumerate(maps_array):
        directory = data[3]
        size = data[1]
        scaling = data[2]

        print(f"map: {data[0]}")

        heightmap = Heightmap("assets" + directory, size, scaling)
        heightmap.get_heightmap_to_array()
        array = heightmap.get_array()
        print("Checking if compressed array is same...")
        print(np.array_equal(array, loaded[f'array_{i}']))



if __name__ == "__main__":
    test_me()
