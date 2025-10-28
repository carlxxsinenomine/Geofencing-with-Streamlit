import math
import folium
import streamlit as st
import streamlit_folium as st_folium
from folium.plugins import Draw
from gps_tracking_control import GPSTrackingControl

# Config for app layout on web
st.set_page_config(layout="wide")

st.title("Geofence Feature")

# Initialize session state for storing named shapes
# Everytime na nag iinteract ang user sa web naga-automatic rerun ang streamlit
# st.session_state jan naka store ung previous state ng app
if 'named_shapes' not in st.session_state:
    st.session_state.named_shapes = []
# Will be used when adding new shapes
if 'pending_name' not in st.session_state:
    st.session_state.pending_name = False
# Stores the unique shape ids
if 'processed_shape_ids' not in st.session_state:
    st.session_state.processed_shape_ids = set()


m = folium.Map(zoom_start=12)


# Haversine formula to find distance between two points on a sphere
# https://www.geeksforgeeks.org/dsa/haversine-formula-to-find-distance-between-two-points-on-a-sphere/
def haversine(lat1, lon1, lat2, lon2):
    # distance between latitudes
    # and longitudes
    dLat = (lat2 - lat1) * math.pi / 180.0
    dLon = (lon2 - lon1) * math.pi / 180.0

    # convert to radians
    lat1 = (lat1) * math.pi / 180.0
    lat2 = (lat2) * math.pi / 180.0

    # apply formulae
    a = (pow(math.sin(dLat / 2), 2) +
         pow(math.sin(dLon / 2), 2) *
         math.cos(lat1) * math.cos(lat2));
    rad = 6371
    c = 2 * math.asin(math.sqrt(a))
    return rad * c

# Update each feature in the named_shapes with its corresponding color based on labels
def update_named_shapes():
    try:
        for feature in st.session_state.named_shapes:
            # If nde pa present sa properties ung color key then proceed
            if not feature.get('properties').get('color'):
                feature['properties']['color'] = get_color_shape(feature['properties']['name'])

            # Folium handles Points and Circles differently than Polygons
            # For circle and point shape
            # Stores the radius into the 'properties'
            if feature.get('geometry', {}).get('type') == 'Point':
                if 'radius' not in feature.get('properties', {}):
                    # Default radius if not provided
                    feature['properties']['radius'] = feature.get('properties', {}).get('radius', 0)

    except (AttributeError, KeyError) as e:
        st.write(f"Error adding features: {e}")

# Accepts a string name for shapes, and returns its respective colors
def get_color_shape(feature_shape):
    lowered_shape_name = feature_shape.lower()
    # For now return color strings maya nalang ung actual colors
    if 'safe area' in lowered_shape_name:
        return 'blue'  # Blue for safe area
    elif 'high risk area' in lowered_shape_name:
        return 'red'  # Red for high risk
    else:
        return 'green'  # Green for evacuation centers etc.

# Function for styling the fence
def shape_style(feature_shape):
    return {
        'fillColor': feature_shape['properties']['color'],
        'color': feature_shape['properties']['color'],
        'weight': 1,
        'fillOpacity': 0.2,
    }

# So here's the plan, all states of the app are stored in the session state
# Meaning if i want to access every property and attribute i can access it through the session state
# the plan? wala putangina
# Here's the plan, whenever the user has drawn shapes on the map,
# Access its features from the 'last_active_drawing'
# Function for saving features into GeoJson format and render it to map
# Some useful links
# https://gis.stackexchange.com/questions/394219/folium-draw-polygons-with-distinct-colours
# https://python-visualization.github.io/folium/latest/user_guide/geojson/geojson.html
# https://leafletjs.com/reference.html#path
def add_shapes_to_map():
    try:
        for feature in st.session_state.named_shapes:
            if feature.get('properties', {}).get('color'):
                geom_type = feature.get('geometry', {}).get('type', '')

                if geom_type == 'Point':
                    coords = feature['geometry']['coordinates']
                    radius = feature.get('properties', {}).get('radius', 0)
                    color = feature['properties']['color']

                    folium.Circle(
                        location=[coords[1], coords[0]],  # [lat, lon]
                        radius=radius,
                        color=color,
                        fill=True,
                        fillColor=color,
                        fillOpacity=0.2,
                        weight=1,
                    ).add_to(m)
                else:
                    # Handle polygons and other shapes
                    folium.GeoJson(
                        data=feature,
                        style_function=shape_style,
                    ).add_to(m)

    except (AttributeError, KeyError) as e:
        st.write(f"Error adding features: {e}")


# Function for saving shape names
def save_properties(is_named, drawing):
    if 'properties' not in drawing:
        drawing['properties'] = {}

    drawing['properties']['is_active'] = False

    # Add name to properties
    if is_named:
        drawing['properties']['name'] = shape_name
    else:
        drawing['properties']['name'] = "Unnamed"

    # For circles, preserve the radius
    if drawing.get('geometry', {}).get('type') == 'Point':
        # The radius is usually stored in properties by the Draw plugin
        if 'radius' not in drawing['properties']:
            drawing['properties']['radius'] = 0  # Default radius

    # Create a unique ID for this shape
    shape_id = f"{drawing['geometry']['type']}_{len(st.session_state.named_shapes)}"
    drawing['properties']['shape_id'] = shape_id

    st.session_state.named_shapes.append(drawing)
    st.session_state.processed_shape_ids.add(shape_id)
    st.session_state.pending_name = False


# Get unique identifier for a drawing
def get_drawing_id(drawing):
    # Create a unique ID based on geometry type and coordinates
    # If drawing is None, or 'geometry' key is not in drawing
    if not drawing or 'geometry' not in drawing:
        return None

    geom = drawing['geometry']
    # geom_type such as Point, Polygon, etc.
    geom_type = geom.get('type', '')
    # Coordinates of each geom object
    coords = str(geom.get('coordinates', ''))
    # To distinguish different shapes with different coordinate points
    return f"{geom_type}_{hash(coords)}"


# Draw plugin for drawing shapes on map layer
# Set polyline and circlemarker as False since hindi naman na sila need(for now)
drawn_shapes = Draw(
    export=False,
    show_geometry_on_click=True,
    draw_options={
        'polyline': False,
        'circlemarker': False,
        'marker': False,
    }
).add_to(m)

# For auto location detection
# Comment this out since we will be using JS for live location tracking
# Since Streamlit can't yet do that without re-running the app everytime a stream of data comes
# rt = folium.plugins.LocateControl(auto_start=True).add_to(m)

# Add shapes to map
add_shapes_to_map()

gps_control = GPSTrackingControl()
m.add_child(gps_control)

# Layout for widgets in col
map_col, output_col = st.columns(2)

with map_col:
    st_data = st_folium.st_folium(m, width=725, key="map")

with output_col:
    all_drawings = st_data.get('all_drawings')

    # Check if a new shape was drawn
    if all_drawings and len(all_drawings) > 0:
        # Get the latest drawing
        latest_drawing = all_drawings[-1]
        drawing_id = get_drawing_id(latest_drawing)

        # Check if drawing_id exists and drawing_id is not yet processed
        if drawing_id and drawing_id not in st.session_state.processed_shape_ids:
            # Only set pending if we're not already pending
            if not st.session_state.pending_name:
                st.session_state.pending_name = True
                st.session_state.current_drawing_id = drawing_id
                st.rerun()

    # Show name input dialog if pending
    if st.session_state.pending_name and all_drawings and len(all_drawings) > 0:
        latest_drawing = all_drawings[-1]
        drawing_id = get_drawing_id(latest_drawing)

        # Verify this is still the shape we're naming
        if drawing_id == st.session_state.get('current_drawing_id'):
            st.subheader("New Shape Drawn")
            # Show preview of what was drawn
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

    # Display all named shapes
    st.subheader("Named Shapes")
    if st.session_state.named_shapes:
        for idx, shape in enumerate(st.session_state.named_shapes):
            shape_type = shape.get('geometry', {}).get('type', 'Unknown')
            shape_name = shape.get('properties', {}).get('name', 'Unnamed')

            with st.expander(f"{idx + 1}. {shape_name} ({shape_type})"):
                st.json(shape)
    else:
        st.info("No shapes drawn yet. Draw a shape on the map to get started!")

    # Show raw all_drawings for debugging
    with st.expander("Raw All Drawings Data"):
        st.write(all_drawings)
    with st.expander("Last Active Drawing"):
        st.write(st_data.get('last_active_drawing'))