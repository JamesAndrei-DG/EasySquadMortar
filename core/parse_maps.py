import re


def parsemaps() -> list:
    with open('./assets/maps.js', 'r') as file:
        javascript_file = file.read()

    name_pattern = r'name:\s*"([^"]*)"'
    size_pattern = r'size:\s*(\d+)'
    scaling_pattern = r'scaling:\s*([\d\.]+)'
    map_url_pattern = r'mapURL:\s*"([^"]*)"'
    max_zoom_level_pattern = r'maxZoomLevel:\s*(\d+)'

    maps = []

    name = re.findall(name_pattern, javascript_file)
    size = re.findall(size_pattern, javascript_file)
    scaling = re.findall(scaling_pattern, javascript_file)
    map_url = re.findall(map_url_pattern, javascript_file)
    max_zoom_level = re.findall(max_zoom_level_pattern, javascript_file)

    for i in range(len(name)):
        map_row = [
            name[i],  # 0
            int(size[i]),  # 1
            float(scaling[i]),  # 2
            map_url[i],  # 3
            int(max_zoom_level[i])  # 4
        ]
        maps.append(map_row)

    return maps
