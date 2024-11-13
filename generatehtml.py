from offline_folium import offline
import folium
import jinja2
from folium.plugins import Realtime




# Create the map object
Base_Map = folium.Map(crs='Simple', zoom_start=4)
albasrah_overlay = folium.raster_layers.ImageOverlay(
    image='albasrah.webp',
    bounds=[[0,0], [-3040,3040]],
    zigzag_index=1
)

albasrah_overlay.add_to(Base_Map)
Base_Map.fit_bounds(bounds=[[0,0], [-3040,3040]])

#Set name for map so we can use javascript to manipulate.
Base_Map._name = "map"
Base_Map._id = "1"


#Add Custom Javascript
el = folium.MacroElement().add_to(Base_Map)
el._template = jinja2.Template("""
    {% macro script(this, kwargs) %}
    // write JS here
    function ZoomOnUpdate(longitude, latitude) {
    map_1.setView([latitude, longitude], 2);  // Set the center to the coordinates and zoom level to 12
}
    {% endmacro %}
""")

#custom javascript
#https://stackoverflow.com/a/58802382

#Base_Map.add_js_link("zoomonmark", "js/zoomonmark.js")


# JavaScript for fetching satellite data and calling zoomonmarker
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
rt.add_to(Base_Map)


# Save the map as an HTML file
Base_Map.save("qt/screen/test.html")
