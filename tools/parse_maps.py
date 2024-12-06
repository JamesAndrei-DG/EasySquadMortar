import re

def parsemaps():
    with open('./assets/assets.js', 'r') as file:
        javascript_file = file.read()

    name_pattern = r'name:\s*"([^"]*)"'
    size_pattern = r'size:\s*(\d+)'
    scaling_pattern = r'scaling:\s*([\d\.]+)'
    mapURL_pattern = r'mapURL:\s*"([^"]*)"'
    maxZoomLevel_pattern = r'maxZoomLevel:\s*(\d+)'

    maps = []

    name = re.findall(name_pattern, javascript_file)
    size = re.findall(size_pattern, javascript_file)
    scaling = re.findall(scaling_pattern, javascript_file)
    mapURL = re.findall(mapURL_pattern, javascript_file)
    maxZoomLevel = re.findall(maxZoomLevel_pattern, javascript_file)

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