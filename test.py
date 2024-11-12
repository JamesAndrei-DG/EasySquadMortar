import folium
from folium.plugins import Realtime
from branca.element import Element

# Create the map object
m = folium.Map()
m._name = "map"
m._id = "1"

# JavaScript for the zoomonmarker function (separate and reusable)
zoomonmarker_js = """
function zoomonmarker(longitude, latitude) {
    // Assuming 'map' is the Leaflet map object, accessible via window.map

    map_1.setView([latitude, longitude], 5);  // Set the center to the coordinates and zoom level to 12
}
"""

# Inject the zoomonmarker function into the map's JavaScript environment
m.get_root().script.add_child(Element(zoomonmarker_js))

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
            // Call the zoomonmarker function here
            zoomonmarker(data.features[0].geometry.coordinates[0], data.features[0].geometry.coordinates[1]);
        })
        .catch(errorHandler);
    }
""")

# Add Realtime plugin to the map
rt = Realtime(source, interval=10000)
rt.add_to(m)

# Save the map as an HTML file
m.save("test.html")
