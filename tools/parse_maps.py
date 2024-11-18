import re

def parse():
    with open('./maps/maps.js', 'r') as file:
        js_template = file.read()

    name_pattern = r'name:\s*"([^"]*)"'
    size_pattern = r'size:\s*(\d+)'
    scaling_pattern = r'scaling:\s*([\d\.]+)'
    mapURL_pattern = r'mapURL:\s*"([^"]*)"'
    maxZoomLevel_pattern = r'maxZoomLevel:\s*(\d+)'

    maps = []

    name = re.findall(name_pattern, js_template)
    size = re.findall(size_pattern, js_template)
    scaling = re.findall(scaling_pattern, js_template)
    mapURL = re.findall(mapURL_pattern, js_template)
    maxZoomLevel = re.findall(maxZoomLevel_pattern, js_template)

    for i in range(len(name)):
        map_row = [
            name[i],  # 0
            int(size[i]),  # 1
            float(scaling[i]),  # 2
            mapURL[i],  # 3
            int(maxZoomLevel[i])  # 4
        ]
        maps.append(map_row)

    return maps