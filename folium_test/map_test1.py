import folium
import shapely
import requests
import streamlit as st
import streamlit_folium
import streamlit_folium as st_folium
from folium import JsCode
from folium.plugins import Realtime
from folium.plugins import Draw

# config for app layout on web
st.set_page_config(layout="wide")

st.title("Geofence Feature")

# Initialize session state for storing named shapes
# Everytime na nag iinteract ang user sa web naga-automatic rerun ang streamlit
# st.session_state jan naka store ung previous state ng app
if 'named_shapes' not in st.session_state:
    st.session_state.named_shapes = []
if 'last_drawing_count' not in st.session_state:
    st.session_state.last_drawing_count = 0
if 'pending_name' not in st.session_state:
    st.session_state.pending_name = False

m = folium.Map(zoom_start=12)

# Accepts a string name for shapes, and returns its respective colors
def get_color_shape(shape_name):
    lowered_shape_name = shape_name.lower()
    # for now return color strings maya nalang ung actual colors
    if 'safe area' in lowered_shape_name:
        return '#647FBC' # blue for sage area
    elif 'high risk area' in lowered_shape_name:
        return '#F75270' # Red for high risk
    else:
        return '#A7E399' # Green for evacuation centers etc.

# So here's the plan, all states of the app are stored in the session state
# meaning if i want to access every property and attribute i can access it through the session state
# the plan? wala putangina
# here's the plan, whenever the user has drawn shapes on the map,
# access its features from the 'last_active_drawing'


# Draw plugin for drawing shapes on map layer
# set polyline, and circlemarker to false since nde naman need
drawn_shapes = Draw(
    export=False,
    show_geometry_on_click=True,
    draw_options={
        'polyline': False,
        'circlemarker': False,
    }
).add_to(m)

# for auto location detection
rt = folium.plugins.LocateControl(auto_start=True).add_to(m)

# layout for widgets in col
map_col, output_col = st.columns(2)

with map_col:
    st_data = st_folium.st_folium(m, width=725, key="map")

with output_col:
    all_drawings = st_data.get('all_drawings')

    # Check if a new shape was drawn
    if all_drawings:
        current_count = len(all_drawings)

        # If new shape detected and not already prompting
        if current_count > st.session_state.last_drawing_count and not st.session_state.pending_name:
            st.session_state.pending_name = True
            st.session_state.last_drawing_count = current_count

    # Show name input dialog if pending
    if st.session_state.pending_name and all_drawings:
        st.subheader("New Shape Drawn")
        shape_name = st.text_input(
            "Enter a name for this shape:",
            key=f"shape_name_{st.session_state.last_drawing_count}",
            placeholder="Enter fence name"
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Save", type="primary"):
                if shape_name:
                    # Get the latest drawing
                    latest_drawing = all_drawings[-1] # gets the last index of the List
                    # Add name to properties
                    if 'properties' not in latest_drawing: # if 'properties' key not in latest_drawing
                        latest_drawing['properties'] = {}
                    latest_drawing['properties']['name'] = shape_name
                    latest_drawing['properties']['is_active'] = False # to check if fence is active or nae

                    # Store in session state
                    st.session_state.named_shapes.append(latest_drawing)
                    st.session_state.pending_name = False
                    st.rerun()
                else:
                    st.warning("Please enter a name!")

        with col2:
            if st.button("Skip"):
                # Add without name
                latest_drawing = all_drawings[-1]
                if 'properties' not in latest_drawing:
                    latest_drawing['properties'] = {}
                latest_drawing['properties']['name'] = "Unnamed"
                latest_drawing['properties']['is_active'] = False  # to check if fence is active or nae
                st.session_state.named_shapes.append(latest_drawing)
                st.session_state.pending_name = False
                st.rerun()

    # Display all named shapes
    st.subheader("Named Shapes")
    if st.session_state.named_shapes:
        for idx, shape in enumerate(st.session_state.named_shapes):
            # get('geometry', {}) if 'geometry' key exist then return its values, else return empty dict {}
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