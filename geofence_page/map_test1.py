import folium
import streamlit as st
import streamlit_folium as st_folium
from folium.plugins import Draw, Fullscreen
from gps_tracking_control import GPSTrackingControl

st.set_page_config(
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("Geofence Feature")

if 'named_shapes' not in st.session_state:
    st.session_state.named_shapes = []
if 'pending_name' not in st.session_state:
    st.session_state.pending_name = False
if 'processed_shape_ids' not in st.session_state:
    st.session_state.processed_shape_ids = set()

st.markdown("""
<style>
    /* Responsive map container */
    .map-container {
        position: relative;
        width: 100%;
        height: 60vh;
        min-height: 400px;
    }

    /* Responsive columns */
    @media (max-width: 768px) {
        .main-column {
            flex-direction: column;
        }
        .stColumn {
            min-width: 100% !important;
        }
    }

    /* Mobile-friendly buttons */
    .mobile-button {
        width: 100%;
        margin: 5px 0;
    }

    /* Responsive text */
    .responsive-text {
        font-size: calc(14px + 0.5vw);
    }
</style>
""", unsafe_allow_html=True)

m = folium.Map(zoom_start=12)
Fullscreen(
    position='topright',
    title='Expand me bitch',
    title_cancel='Exit kana?',
    force_separate_button=True
).add_to(m)

# Update each feature in the named_shapes with its corresponding color based on labels
def update_named_shapes():
    try:
        for feature in st.session_state.named_shapes:
            if not feature.get('properties').get('color'):
                feature['properties']['color'] = get_color_shape(feature['properties']['name'])

            if feature.get('geometry', {}).get('type') == 'Point':
                if 'radius' not in feature.get('properties', {}):
                    feature['properties']['radius'] = feature.get('properties', {}).get('radius', 0)
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
                    radius = feature.get('properties', {}).get('radius', 0)
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
            drawing['properties']['radius'] = 0

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


# Draw plugin for drawing shapes on map layer
drawn_shapes = Draw(
    export=False,
    show_geometry_on_click=True,
    draw_options={
        'polyline': False,
        'circlemarker': False,
        'marker': False,
    }
).add_to(m)

gps_control = GPSTrackingControl(st.session_state.named_shapes)
m.add_child(gps_control)

add_shapes_to_map()

st.markdown('<div class="main-column">', unsafe_allow_html=True)

map_col, output_col = st.columns([2, 1])

with map_col:
    with st.container():
        st.markdown("### Map")
        map_width = min(800, st.session_state.get('screen_width', 725))
        st_data = st_folium.st_folium(m, width=None, height=500, key="map")

with output_col:
    st.markdown("### Controls & Information")

    all_drawings = st_data.get('all_drawings')

    # Check if a new shape was drawn
    if all_drawings and len(all_drawings) > 0:
        latest_drawing = all_drawings[-1]
        drawing_id = get_drawing_id(latest_drawing)

        if drawing_id and drawing_id not in st.session_state.processed_shape_ids:
            if not st.session_state.pending_name:
                st.session_state.pending_name = True
                st.session_state.current_drawing_id = drawing_id
                st.rerun()

    # Show name input dialog if pending
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
                if st.button("Save", type="primary", use_container_width=True):
                    if shape_name:
                        save_properties(True, latest_drawing)
                        update_named_shapes()
                        st.rerun()
                    else:
                        st.warning("Please enter a name!")
            with col2:
                if st.button("Skip", use_container_width=True):
                    save_properties(False, latest_drawing)
                    update_named_shapes()
                    st.rerun()

    st.subheader("Named Shapes")
    if st.session_state.named_shapes:
        for idx, shape in enumerate(st.session_state.named_shapes):
            shape_type = shape.get('geometry', {}).get('type', 'Unknown')
            shape_name = shape.get('properties', {}).get('name', 'Unnamed')

            with st.expander(f"{idx + 1}. {shape_name} ({shape_type})", expanded=False):
                st.code(str(shape), language='json')
    else:
        st.info("No shapes drawn yet. Draw a shape on the map to get started!")

    with st.expander("Raw All Drawings Data"):
        st.code(str(all_drawings), language='json')

    with st.expander("Last Active Drawing"):
        st.code(str(st_data.get('last_active_drawing')), language='json')

st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)