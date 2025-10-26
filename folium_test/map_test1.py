import folium
import streamlit as st
import streamlit_folium as st_folium
from folium.plugins import Draw
from branca.element import MacroElement, Template

# Config for app layout on web
st.set_page_config(layout="wide")

st.title("Geofence Feature with Real-time GPS")

# Initialize session state
if 'named_shapes' not in st.session_state:
    st.session_state.named_shapes = []
if 'pending_name' not in st.session_state:
    st.session_state.pending_name = False
if 'processed_shape_ids' not in st.session_state:
    st.session_state.processed_shape_ids = set()

m = folium.Map(zoom_start=12)


def update_named_shapes():
    try:
        for feature in st.session_state.named_shapes:
            if not feature.get('properties').get('color'):
                feature['properties']['color'] = get_color_shape(feature['properties']['name'])

            if feature.get('geometry', {}).get('type') == 'Point':
                if 'radius' not in feature.get('properties', {}):
                    feature['properties']['radius'] = feature.get('properties', {}).get('radius', 100)
    except (AttributeError, KeyError) as e:
        st.write(f"Error adding features: {e}")


def get_color_shape(feature_shape):
    lowered_shape_name = feature_shape.lower()
    if 'safe area' in lowered_shape_name:
        return 'blue'
    elif 'high risk area' in lowered_shape_name:
        return 'red'
    else:
        return 'green'


def shape_style(feature_shape):
    return {
        'fillColor': feature_shape['properties']['color'],
        'color': feature_shape['properties']['color'],
        'weight': 1,
        'fillOpacity': 0.2,
    }


def add_shapes_to_map():
    try:
        for feature in st.session_state.named_shapes:
            if feature.get('properties', {}).get('color'):
                geom_type = feature.get('geometry', {}).get('type', '')

                if geom_type == 'Point':
                    coords = feature['geometry']['coordinates']
                    radius = feature.get('properties', {}).get('radius', 100)
                    color = feature['properties']['color']

                    folium.Circle(
                        location=[coords[1], coords[0]],
                        radius=radius,
                        color=color,
                        fill=True,
                        fillColor=color,
                        fillOpacity=0.2,
                        weight=1,
                    ).add_to(m)
                else:
                    folium.GeoJson(
                        data=feature,
                        style_function=shape_style,
                    ).add_to(m)
    except (AttributeError, KeyError) as e:
        st.write(f"Error adding features: {e}")


def save_properties(is_named, drawing):
    if 'properties' not in drawing:
        drawing['properties'] = {}

    drawing['properties']['is_active'] = False

    if is_named:
        drawing['properties']['name'] = shape_name
    else:
        drawing['properties']['name'] = "Unnamed"

    if drawing.get('geometry', {}).get('type') == 'Point':
        if 'radius' not in drawing['properties']:
            drawing['properties']['radius'] = 100

    shape_id = f"{drawing['geometry']['type']}_{len(st.session_state.named_shapes)}"
    drawing['properties']['shape_id'] = shape_id

    st.session_state.named_shapes.append(drawing)
    st.session_state.processed_shape_ids.add(shape_id)
    st.session_state.pending_name = False


def get_drawing_id(drawing):
    if not drawing or 'geometry' not in drawing:
        return None

    geom = drawing['geometry']
    geom_type = geom.get('type', '')
    coords = str(geom.get('coordinates', ''))

    return f"{geom_type}_{hash(coords)}"


# Custom GPS Tracking Control using MacroElement
class GPSTrackingControl(MacroElement):
    _template = Template("""
        {% macro script(this, kwargs) %}
            var locationMarker_{{ this.get_name() }} = null;
            var accuracyCircle_{{ this.get_name() }} = null;
            var pathLine_{{ this.get_name() }} = null;
            var pathCoordinates_{{ this.get_name() }} = [];
            var isTracking_{{ this.get_name() }} = false;
            var watchId_{{ this.get_name() }} = null;

            function startTracking_{{ this.get_name() }}() {
                if (!navigator.geolocation) {
                    alert('Geolocation is not supported by your browser');
                    return;
                }

                isTracking_{{ this.get_name() }} = true;
                document.getElementById('trackingStatus_{{ this.get_name() }}').innerHTML = '🟢 Tracking Active';
                document.getElementById('trackingStatus_{{ this.get_name() }}').style.color = 'green';

                watchId_{{ this.get_name() }} = navigator.geolocation.watchPosition(
                    function(position) {
                        var lat = position.coords.latitude;
                        var lng = position.coords.longitude;
                        var accuracy = position.coords.accuracy;

                        if (locationMarker_{{ this.get_name() }}) {
                            {{ this._parent.get_name() }}.removeLayer(locationMarker_{{ this.get_name() }});
                        }
                        if (accuracyCircle_{{ this.get_name() }}) {
                            {{ this._parent.get_name() }}.removeLayer(accuracyCircle_{{ this.get_name() }});
                        }

                        locationMarker_{{ this.get_name() }} = L.marker([lat, lng], {
                            icon: L.divIcon({
                                className: 'custom-location-marker',
                                html: '<div style="background-color: #2A93EE; width: 16px; height: 16px; border-radius: 50%; border: 3px solid white; box-shadow: 0 0 10px rgba(0,0,0,0.5);"></div>',
                                iconSize: [16, 16],
                                iconAnchor: [8, 8]
                            })
                        }).addTo({{ this._parent.get_name() }});

                        accuracyCircle_{{ this.get_name() }} = L.circle([lat, lng], {
                            radius: accuracy,
                            color: '#136AEC',
                            fillColor: '#2A93EE',
                            fillOpacity: 0.15,
                            weight: 2
                        }).addTo({{ this._parent.get_name() }});

                        pathCoordinates_{{ this.get_name() }}.push([lat, lng]);

                        if (pathLine_{{ this.get_name() }}) {
                            {{ this._parent.get_name() }}.removeLayer(pathLine_{{ this.get_name() }});
                        }
                        if (pathCoordinates_{{ this.get_name() }}.length > 1) {
                            pathLine_{{ this.get_name() }} = L.polyline(pathCoordinates_{{ this.get_name() }}, {
                                color: 'blue',
                                weight: 3,
                                opacity: 0.7
                            }).addTo({{ this._parent.get_name() }});
                        }

                        {{ this._parent.get_name() }}.setView([lat, lng], {{ this._parent.get_name() }}.getZoom());

                        document.getElementById('coordinates_{{ this.get_name() }}').innerHTML = 
                            'Lat: ' + lat.toFixed(6) + ', Lng: ' + lng.toFixed(6) + 
                            '<br>Accuracy: ±' + accuracy.toFixed(0) + 'm';
                    },
                    function(error) {
                        console.error('Error getting location:', error);
                        document.getElementById('trackingStatus_{{ this.get_name() }}').innerHTML = '❌ Error: ' + error.message;
                        document.getElementById('trackingStatus_{{ this.get_name() }}').style.color = 'red';
                    },
                    {
                        enableHighAccuracy: true,
                        maximumAge: 0,
                        timeout: 5000
                    }
                );
            }

            function stopTracking_{{ this.get_name() }}() {
                if (watchId_{{ this.get_name() }} !== null) {
                    navigator.geolocation.clearWatch(watchId_{{ this.get_name() }});
                    watchId_{{ this.get_name() }} = null;
                }
                isTracking_{{ this.get_name() }} = false;
                document.getElementById('trackingStatus_{{ this.get_name() }}').innerHTML = '🔴 Tracking Stopped';
                document.getElementById('trackingStatus_{{ this.get_name() }}').style.color = 'red';
            }

            function clearPath_{{ this.get_name() }}() {
                if (pathLine_{{ this.get_name() }}) {
                    {{ this._parent.get_name() }}.removeLayer(pathLine_{{ this.get_name() }});
                    pathLine_{{ this.get_name() }} = null;
                }
                pathCoordinates_{{ this.get_name() }} = [];
            }

            function toggleTracking_{{ this.get_name() }}() {
                if (isTracking_{{ this.get_name() }}) {
                    stopTracking_{{ this.get_name() }}();
                } else {
                    startTracking_{{ this.get_name() }}();
                }
            }

            var GPSControl_{{ this.get_name() }} = L.Control.extend({
                options: {
                    position: 'topleft'
                },
                onAdd: function(map) {
                    var container = L.DomUtil.create('div', 'leaflet-bar leaflet-control');
                    container.style.background = 'white';
                    container.style.padding = '10px';
                    container.style.borderRadius = '5px';
                    container.style.boxShadow = '0 2px 5px rgba(0,0,0,0.3)';

                    container.innerHTML = `
                        <div style="margin-bottom: 5px;">
                            <button onclick="toggleTracking_{{ this.get_name() }}()" 
                                    style="padding: 8px 15px; cursor: pointer; background: #2A93EE; color: white; border: none; border-radius: 3px; font-weight: bold;">
                                Start/Stop GPS
                            </button>
                            <button onclick="clearPath_{{ this.get_name() }}()" 
                                    style="padding: 8px 15px; cursor: pointer; background: #FF6B6B; color: white; border: none; border-radius: 3px; margin-left: 5px;">
                                Clear Path
                            </button>
                        </div>
                        <div id="trackingStatus_{{ this.get_name() }}" style="font-weight: bold; margin-top: 5px;">⚪ Not Tracking</div>
                        <div id="coordinates_{{ this.get_name() }}" style="font-size: 12px; margin-top: 5px; color: #666;"></div>
                    `;

                    L.DomEvent.disableClickPropagation(container);
                    return container;
                }
            });

            {{ this._parent.get_name() }}.addControl(new GPSControl_{{ this.get_name() }}());
        {% endmacro %}
    """)

    def __init__(self):
        super(GPSTrackingControl, self).__init__()
        self._name = 'GPSTrackingControl'


# Draw plugin
drawn_shapes = Draw(
    export=False,
    show_geometry_on_click=True,
    draw_options={
        'polyline': False,
        'circlemarker': False,
    }
).add_to(m)

# Add shapes to map
add_shapes_to_map()

# Add GPS Tracking Control
gps_control = GPSTrackingControl()
m.add_child(gps_control)

# Layout
map_col, output_col = st.columns(2)

with map_col:
    st.info("🎯 Click 'Start/Stop GPS' button on the map to begin real-time tracking")
    st_data = st_folium.st_folium(m, width=725, height=600, key="map")

with output_col:
    st.subheader("GPS Tracking Info")
    st.write("""
    **How to use:**
    1. Click the **"Start/Stop GPS"** button on the map (top-left corner)
    2. Allow location access when prompted by your browser
    3. Your location will update automatically every few seconds
    4. The blue line shows your movement path
    5. Click **"Clear Path"** to reset the trail

    **Note:** This uses JavaScript for true real-time updates without page refresh!
    """)

    st.divider()

    # Shape drawing section
    all_drawings = st_data.get('all_drawings')

    if all_drawings and len(all_drawings) > 0:
        latest_drawing = all_drawings[-1]
        drawing_id = get_drawing_id(latest_drawing)

        if drawing_id and drawing_id not in st.session_state.processed_shape_ids:
            if not st.session_state.pending_name:
                st.session_state.pending_name = True
                st.session_state.current_drawing_id = drawing_id
                st.rerun()

    if st.session_state.pending_name and all_drawings and len(all_drawings) > 0:
        latest_drawing = all_drawings[-1]
        drawing_id = get_drawing_id(latest_drawing)

        if drawing_id == st.session_state.get('current_drawing_id'):
            st.subheader("New Shape Drawn")
            shape_type = latest_drawing.get('geometry', {}).get('type', 'Unknown')
            st.info(f"Shape type: {shape_type}")

            shape_name = st.text_input(
                "Enter a name for this shape:",
                key=f"shape_name_{drawing_id}",
                placeholder="Enter fence name"
            )

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Save", type="primary"):
                    if shape_name:
                        save_properties(True, latest_drawing)
                        update_named_shapes()
                        st.rerun()
                    else:
                        st.warning("Please enter a name!")

            with col2:
                if st.button("Skip"):
                    save_properties(False, latest_drawing)
                    update_named_shapes()
                    st.rerun()

    st.subheader("Named Shapes")
    if st.session_state.named_shapes:
        for idx, shape in enumerate(st.session_state.named_shapes):
            shape_type = shape.get('geometry', {}).get('type', 'Unknown')
            shape_name = shape.get('properties', {}).get('name', 'Unnamed')

            with st.expander(f"{idx + 1}. {shape_name} ({shape_type})"):
                st.json(shape)
    else:
        st.info("No shapes drawn yet. Draw a shape on the map to get started!")

    with st.expander("Debug: Raw All Drawings"):
        st.write(all_drawings)
    with st.expander("Debug: Last Active Drawing"):
        st.write(st_data.get('last_active_drawing'))