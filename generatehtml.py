import folium
import jinja2
from folium.plugins import Realtime
import re


def parse_maps():
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


maps_array = parse_maps()

for i, data in enumerate(maps_array):
    # Create the map object
    base_map = folium.Map(crs='Simple', zoom_start=4)
    map_overlay = folium.raster_layers.ImageOverlay(
        image=str("./maps" + data[3] + "basemap.webp"),
        bounds=[[0, 0], [-int(data[1]), int(data[1])]],
        zigzag_index=1
    )

    map_overlay.add_to(base_map)
    base_map.fit_bounds(bounds=[[0, 0], [-int(data[1]), int(data[1])]])

    # Set name for map so we can use javascript to manipulate.
    base_map._name = "map"
    base_map._id = "1"

    # Add Custom Javascript after map creation
    el = folium.MacroElement().add_to(base_map)
    el._template = jinja2.Template("""
        {% macro script(this, kwargs) %}
        // write JS here
        function ZoomOnUpdate(longitude, latitude) {
        map_1.setView([latitude, longitude], 2);  // Set the center to the coordinates and zoom level to 12
    }
        {% endmacro %}
    """)

    # custom javascript
    # https://stackoverflow.com/a/58802382

    # JavaScript for fetching satellite data and added zoomonmarker function call
    source = folium.JsCode("""
        function(responseHandler, errorHandler) {
            var url = 'https://api.wheretheiss.at/v1/satellites/25544';
            
            fetch(url)
            .then((response) => {
                return response.json().then((data) => {
                    var { id, longitude, latitude } = data;
    
                    return {
                        'type': 'FeatureCollection',
                        'features': [{
                            'type': 'Feature',
                            'geometry': {
                                'type': 'Point',
                                'coordinates': [longitude, latitude]
                            },
                            'properties': {
                                'id': id
                            }
                        }]
                    };
                })
            })
            .then((data) => {
                responseHandler(data);
                // Call the ZoomOnUpdate function here
                ZoomOnUpdate(data.features[0].geometry.coordinates[0], data.features[0].geometry.coordinates[1]);
            })
            .catch(errorHandler);
        }
    """)

    # Add Realtime plugin to the map
    rt = Realtime(source, interval=10000)
    rt.add_to(base_map)

    # Save the map as an HTML file
    base_map.save(str("qt/screen/maps/" + data[0] + ".html"))
