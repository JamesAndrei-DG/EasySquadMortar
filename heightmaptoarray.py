import cv2
import time
import tracemalloc
import numpy as np


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

        # Display results with high precision
        print(f"Function '{func.__name__}' executed in {end_time - start_time:.10f} seconds.")
        print(f"Current memory usage: {current / 1024:.2f} KB")
        print(f"Peak memory usage: {peak / 1024:.2f} KB")

        return result

    return wrapper


class Heightmap:
    def __init__(self, image_path):
        # Load the image
        self.image = cv2.imread(image_path, cv2.IMREAD_COLOR)
        self.height, self.width, _ = self.image.shape

        self.scaling_xysizeratio = (self.height) / 4617 #heightmapsize / original size assuming map is square
        self.scaling_height = 0.733125 #based on map Scaling attribute

        print(f"height: {self.height}\nwidth: {self.width}")
        self.array = np.zeros((4617,4617),dtype=np.float16) #array should be size of original map

        #buffer x and y
        self.buffer_x = 0
        self.buffer_y = 0
        self.buffer_height = 0


    def get_height(self, find_x, find_y):
        # Adjust coordinates based on scaling
        # Warning: We don't check if coordinates are valid
        scaled_x = round(find_x * self.scaling_xysizeratio)
        scaled_y = round(find_y * self.scaling_xysizeratio)  # origin_y-axis inversion

        if not (0 <= scaled_x < self.width and 0 <= scaled_y < self.height):
            return 0

        if self.buffer_x == scaled_x and self.buffer_y == scaled_y:
            return self.buffer_height

        # Color (B, G, R)

        # print(f"scaled x={scaled_x},y={scaled_y}")
        color = self.image[scaled_y, scaled_x]

        # Calculate height
        if int(color[2]) + int(color[0]) <= 10:  #black does not show as all 0
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


    @timer_and_memory
    def get_heightmap_to_array(self):
        #for changing y
        for x in range(self.array.shape[0]):
            for y in range(self.array.shape[1]):
                # print(f"original x:{x}y:{y}")
                self.array[x][y] = self.get_height(x,y)

    def save_array(self):
        np.save('data.npy',self.array)

    @timer_and_memory
    def load_array(self):
        self.array = np.load('data.npy')

    def get_height_from_array(self, x ,y):
        print(f"array\nheight @[{x}][{y}]: {self.array[x][y]}")

    def get_height_from_map(self, x, y):
        height = self.get_height(x,y)
        print(f"heightmap\nheight @[{x}][{y}]: {height}")






    # Example usage
heightmap = Heightmap("maps/kohat/heightmap.webp")
heightmap.get_heightmap_to_array()
heightmap.save_array()
# heightmap.load_array()
# heightmap.get_height_from_array(2444,1500)
# heightmap.get_height_from_map(2444,1500)
# heightmap.get_height(2444,1500)
