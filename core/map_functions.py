import math
from time import perf_counter
import os
import sys
import numpy as np
from scipy.interpolate import LinearNDInterpolator


def _natomils2rad(natomils: int) -> float:
    """
    Converts a given value in mils (NATO mils) to radians.

    Args:
        natomils (int): The value in NATO mils to be converted.

    Returns:
        float: The equivalent value in radians.
    """
    return natomils * 0.981719 * 0.001


def _azimuth2rad(azimuth_f: float) -> float:
    """
    Converts an azimuth angle in degrees to radians.

    Args:
        azimuth_f (float): The azimuth angle in degrees.

    Returns:
        float: The equivalent value in radians.
    """
    return azimuth_f * math.pi / 180


def _validate_inputs(azimuth_f: float, natomils: int) -> None:
    """Validates the input parameters."""
    if natomils < 800 or natomils > 1580:
        raise ValueError(f"{natomils} is an invalid input in natomils")
    elif azimuth_f < 0 or azimuth_f > 359:
        raise ValueError(f"{azimuth_f} is an invalid input in azimuth")


class MapFunction:
    def __init__(self):

        if getattr(sys, 'frozen', False):
            with np.load(
                    os.path.join(os.path.dirname(sys.executable), "core", "arrays",
                                 "map_arrays_compressed.npz")) as map_data:
                self.map_data = map_data
                self.current_map = self.map_data["array_0"]  # Default to Al Basrah

        else:
            with np.load("core/arrays/map_arrays_compressed.npz") as map_data:
                self.map_data = map_data
                self.current_map = self.map_data["array_0"]  # Default to Al Basrah
        self.precalculated_firing_solution = []
        self.origin_x = 0
        self.origin_y = 0
        self.precalculated = False

    def change_map(self, map_index: int) -> None:
        """
        Changes the current map to the specified index.
    
        Args:
            map_index (int): Index of the map to load from the compressed map data.
        """
        print("Changing current map")
        self.current_map = self.map_data[f"array_{map_index}"]

    def set_origin_xy(self, x: int, y: int) -> None:
        """
        Sets the origin coordinates for calculations and triggers firing solution pre-calculation.
    
        Args:
            x (int): X-coordinate for the origin.
            y (int): Y-coordinate for the origin.
        """
        print(f"Setting origin to ({x}, {y})")
        self.origin_x = x
        self.origin_y = y
        self._precalculate_firing_solution()

    def set_origin_keypad(self, keypad: str) -> None:
        """
        Sets the origin coordinates using a keypad input and triggers firing solution pre-calculation.
    
        Args:
            keypad (str): Keypad string specifying the origin (e.g., "A1-5-2-8-5").
        """
        print(f"Setting origin using keypad: {keypad}")
        self.origin_x, self.origin_y = self.get_keypad_position(keypad)
        print(f"Calculated origin: x={self.origin_x}, y={self.origin_y}")
        self._precalculate_firing_solution()

    def get_keypad_position(self, keypad: str) -> tuple[int, int]:
        """
        Calculates the position (x, y) based on a keypad input.
    
        Args:
            keypad (str): Keypad string specifying the position (e.g., "A1-5-2-8-5").
    
        Returns:
            tuple[int, int]: Calculated coordinates (x, y).
        """
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
            raise Exception(f"Error in get_keypad_position: {error}")

    def get_height(self, x: int, y: int) -> float:
        """
        Retrieves the height value from the current map at the specified coordinates.
        
        Args:
            x (int): The x-coordinate on the map.
            y (int): The y-coordinate on the map.
        
        Returns:
            float: The height value at the given coordinates. Returns 0 if the coordinates are out of bounds.
        """
        try:
            return self.current_map[x][y]
        except IndexError:
            print(f"Coordinates out of bounds: x={x}, y={y}")
            return 0
        except Exception as error:
            raise Exception(f"Error in get_height: {error}")

    def get_distance(self, rad: float, elevation_array: list[tuple[float, int, int]]) -> tuple[float, int, int]:
        """
        Calculates the distance, x, and y coordinates at which a projectile intersects with the ground.
        
        Args:
            rad (float): The firing angle in radians.
            elevation_array (list[tuple[float, int, int]]): A list of tuples containing elevation, x, and y coordinates.
        
        Returns:
            tuple[float, int, int]: A tuple containing the distance, x, and y coordinates of the impact point.
        """
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

    def _find_xy_from_origin(self, azimuth_f: float, distance: float) -> tuple[int, int]:
        """
        Calculates the (x, y) coordinates based on the origin, azimuth angle, and distance.
        
        Args:
            azimuth_f (float): Azimuth angle in degrees.
            distance (float): Distance from the origin.
        
        Returns:
            tuple[int, int]: Coordinates (x, y) calculated from the given parameters.
        """
        rad = _azimuth2rad(azimuth_f)
        x_scale = np.sin(rad)
        y_scale = np.cos(rad)
        x_find = int(self.origin_x + distance * x_scale)
        y_find = int(self.origin_y - distance * y_scale)
        return x_find, y_find

    def _precalculate_firing_solution(self) -> None:
        """
        Precalculates the firing solution for all azimuth angles and stores the results.
        
        This method initializes the firing solution calculation, iterates over all azimuth
        angles from 0 to 359, and appends the results of distance calculations for each azimuth.
        The process is timed and the duration is printed for performance measurement.
        
        The `precalculated` attribute is set to False before calculation starts and set to True
        once the calculation finishes.
        """
        self.precalculated = False
        print("Precalculating firing solution")
        t1 = perf_counter()
        for azimuth in range(360):
            self.precalculated_firing_solution.append(self._calculate_all_possible_distances_from_azimuth(azimuth))
        t2 = perf_counter()
        time = (t2 - t1) * 1000
        print(f"Calculation Finished in {time} ms")
        self.precalculated = True

    def _calculate_all_possible_distances_from_azimuth(self, azimuth: int) -> list[tuple[float, int, int]]:
        """
        Calculates all possible impact distances for a given azimuth angle.
        
        Args:
            azimuth (int): The azimuth angle in degrees for which distances are to be calculated.
        
        Returns:
            list[tuple[float, int, int]]: A list of tuples, where each tuple contains:
                - The distance to the impact point.
                - The x-coordinate of the impact point.
                - The y-coordinate of the impact point.
        """
        result = []
        elevation_range = self._calculate_elevation_range_from_azimuth(azimuth)
        for natomil in range(800, 1580 + 1, 10):
            result.append(self.get_distance(_natomils2rad(natomil), elevation_range))
        return result

    def _calculate_elevation_range_from_azimuth(self, azimuth: float) -> list[tuple[float, int, int]]:
        """
        Calculates the elevation and coordinates for a range of points along a specified azimuth.
        
        Converts the azimuth angle in degrees to radians, then calculates the
        height, x, and y coordinates along a straight line extending from the origin
        over a range of 0 to 1500 meters in 10-meter steps.
        
        Args:
            azimuth (float): The azimuth angle in degrees.
        
        Returns:
            list[tuple[float, int, int]]: A list of tuples where each tuple contains:
                - float: The height value from the current map at the calculated coordinates.
                - int: The x-coordinate on the map for the current point.
                - int: The y-coordinate on the map for the current point.
        """
        rad = _azimuth2rad(azimuth)
        x_scale = np.sin(rad)
        y_scale = np.cos(rad)
        height_array = []

        for meters in range(0, 1500 + 1, 10):
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
        """Calculates coordinates based on azimuth and natomils."""
        try:
            # Validate inputs
            _validate_inputs(azimuth_f, natomils)

            if not self.precalculated:
                # Calculate
                elevation_array = self._calculate_elevation_range_from_azimuth(azimuth_f)
                distance, x, y = self.get_distance(_natomils2rad(natomils), elevation_array)
                return x, y

            # Perform interpolation using precalculated firing solutions
            i1 = max(0, int((natomils - 800) / 10))
            i2 = i1 + 1
            az1 = int(azimuth_f)
            if az1 == 359:
                az2 = 0
            else:
                az2 = int(azimuth_f + 1)

            distance1 = (self.precalculated_firing_solution[az1][i1][0] + self.precalculated_firing_solution[az2][i1][
                0]) / 2
            distance2 = (self.precalculated_firing_solution[az1][i2][0] + self.precalculated_firing_solution[az2][i2][
                0]) / 2
            # Linear interpolation
            distance = distance1 + (distance2 - distance1) * (natomils % 10) / 10
            return self._find_xy_from_origin(azimuth_f, distance)

        except Exception as error:
            raise RuntimeError(f"Error encountered in shoot_distance: {error}")
