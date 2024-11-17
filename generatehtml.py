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

    # Add Custom Javascript Files
    base_map.add_js_link("zoom-on-update", "./javascript/zoom-on-update.js")
    base_map.add_js_link("GeoSSE", "./javascript/Leaflet.GeoSSE.min.js")

    # Custom Javascript
    # https://stackoverflow.com/a/58802382
    javascript = folium.MacroElement().add_to(base_map)
    javascript._template = jinja2.Template("""
            {% macro script(this, kwargs) %}
            
            //SSE Client Setup
            var geoSSELayer = L.geoSSE(null, {
            streamUrl: "http://127.0.0.1:8000/impact-point",
            featureIdField: "id",
            });
            map_1.addLayer(geoSSELayer);
            geoSSELayer.connectToEventStream();
            
            {% endmacro %}
        """)

    # Save the map as an HTML file
    base_map.save(str("qt/screen/maps/" + data[0] + ".html"))
