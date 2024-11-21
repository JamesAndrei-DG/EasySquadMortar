import folium
import jinja2
from folium.plugins import Realtime
from tools import parse_maps

maps_array = parse_maps.parse()

for i, data in enumerate(maps_array):
    base_map = folium.Map(crs='Simple', zoom_start=4)
    map_overlay = folium.raster_layers.ImageOverlay(
        image=str("./maps" + data[3] + "basemap.webp"),
        bounds=[[0, 0], [-int(data[1]), int(data[1])]],
        zigzag_index=1,
        zoom_control=False,
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
    base_map.save(str("qt/components/maps/" + data[0] + ".html"))
