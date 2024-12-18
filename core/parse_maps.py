import re
import os
import sys

# Constants for Regular Expression Patterns
NAME_PATTERN = r'name:\s*"([^"]*)"'
SIZE_PATTERN = r'size:\s*(\d+)'
SCALING_PATTERN = r'scaling:\s*([\d\.]+)'
MAP_URL_PATTERN = r'mapURL:\s*"([^"]*)"'
MAX_ZOOM_PATTERN = r'maxZoomLevel:\s*(\d+)'


def parse_maps() -> list:
    """
    Parses the maps.js file to extract map details such as names, sizes, scalings, URLs, and max zoom levels.

    Returns:
        list: A list of maps, where each map is represented as a list containing the following information:
            - Name (str): The name of the map.
            - Size (str): The size of the map.
            - Scaling (str): The scaling factor of the map.
            - Map URL (str): The URL of the map image.
            - Max Zoom Level (str): The maximum zoom level of the map.
    """

    if getattr(sys, 'frozen', False):
        with open(os.path.join(os.path.dirname(sys.executable), 'assets', 'maps.js'), 'r') as file: #fix error
            javascript_file = file.read()
    else:
        with open('./assets/maps.js', 'r') as file:
            javascript_file = file.read()

    names = re.findall(NAME_PATTERN, javascript_file)
    sizes = re.findall(SIZE_PATTERN, javascript_file)
    scalings = re.findall(SCALING_PATTERN, javascript_file)
    map_urls = re.findall(MAP_URL_PATTERN, javascript_file)
    max_zoom_levels = re.findall(MAX_ZOOM_PATTERN, javascript_file)

    map_data = []
    for i in range(len(names)):
        map_details = [
            names[i],  # 0: Name
            sizes[i],  # 1: Size
            scalings[i],  # 2: Scaling
            map_urls[i],  # 3: Map URL
            max_zoom_levels[i]  # 4: Max Zoom Level
        ]
        map_data.append(map_details)

    return map_data
