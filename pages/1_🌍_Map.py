import folium
import pymongo
import streamlit as st
import streamlit_folium as st_folium

from folium.plugins import Draw, Fullscreen

import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from map.gps_tracking_control import GPSTrackingControl

st.set_page_config(
    page_title="Map",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

m = folium.Map(zoom_start=12)
Fullscreen(
    position='topright',
    title='Expand me bitch',
    title_cancel='Exit kana?',
    force_separate_button=True
).add_to(m)

# Draw plugin for drawing shapes on maps layer
drawn_shapes = Draw(
    export=False,
    show_geometry_on_click=True,
    draw_options={
        'polyline': True,
        'circlemarker': False,
        'marker': False,
    },
    edit_options={
        'edit': False,
        'remove': False
    }
).add_to(m)

# MongoDB configuration
@st.cache_resource
def init_connection():
    try:
        # Add timeout parameters
        client = pymongo.MongoClient(
            st.secrets["mongo"],
            serverSelectionTimeoutMS=5000,  # 5 second timeout
            connectTimeoutMS=5000,
            socketTimeoutMS=5000
        )
        # Test the connection
        client.admin.command('ping')
        geo_db = client.geospatial_data
        return {
            'shapes_collection': geo_db.shapes,
            'user_collection': geo_db.user,
            'trail_collection': geo_db.user_trail
        }
    except pymongo.errors.ConfigurationError:
        st.error("⚠️ **MongoDB Configuration Error**")
        st.error("Please check your connection string in Streamlit secrets.")
        st.info("Go to: Settings → Secrets → Add your MongoDB connection string as 'mongo'")
        st.stop()
    except pymongo.errors.ServerSelectionTimeoutError:
        st.error("⚠️ **Cannot Connect to MongoDB**")
        st.error("Please verify:")
        st.markdown("""
        - ✓ MongoDB server is running
        - ✓ Connection string is correct
        - ✓ Network access is configured (whitelist IP: `0.0.0.0/0` for Streamlit Cloud)
        - ✓ Database user has proper permissions
        """)
        st.stop()
    except KeyError:
        st.error("⚠️ **Missing MongoDB Secret**")
        st.error("No 'mongo' key found in Streamlit secrets.")
        st.info("Add your MongoDB connection string in: **Settings → Secrets**")
        st.code('mongo = "your_connection_string_here"', language="toml")
        st.stop()
    except Exception as e:
        st.error(f"⚠️ **Unexpected Error**: {type(e).__name__}")
        st.error(str(e))
        st.stop()

# Initialize connection
db_collections = init_connection()
shapes = db_collections['shapes_collection']
trail_collection = db_collections['trail_collection']

# Initialize session state with error handling
if 'named_shapes' not in st.session_state:
    try:
        st.session_state.named_shapes = [
            {'type': shape['type'],
             'properties': shape['properties'],
             'geometry': shape['geometry']}
            for shape in shapes.find()
        ]
    except Exception as e:
        st.warning(f"⚠️ Could not load existing shapes: {str(e)}")
        st.info("Starting with empty shapes list. You can still draw new shapes.")
        st.session_state.named_shapes = []

if 'pending_name' not in st.session_state:
    st.session_state.pending_name = False
if 'processed_shape_ids' not in st.session_state:
    st.session_state.processed_shape_ids = set()

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

    drawing_to_save = drawing.copy()
    if '_id' in drawing_to_save:
        del drawing_to_save['_id']

    try:
        result = shapes.insert_one(drawing_to_save)
        drawing_to_save['_id'] = str(result.inserted_id)
    except Exception as e:
        st.error(f"Error saving to database: {e}")
        return

    # Save to session_state
    st.session_state.named_shapes.append(drawing_to_save)
    st.session_state.processed_shape_ids.add(shape_id)
    st.session_state.pending_name = False

    update_named_shapes()
    st.rerun()


def get_drawing_id(drawing):
    if not drawing or 'geometry' not in drawing:
        return None
    geom = drawing['geometry']
    geom_type = geom.get('type', '')
    coords = str(geom.get('coordinates', ''))
    return f"{geom_type}_{hash(coords)}"

update_named_shapes()
add_shapes_to_map()

gps_control = GPSTrackingControl(st.session_state.named_shapes)
m.add_child(gps_control)

# for shape in shapes.find():
#     print(shape)
# geojson_data = {'type': 'Feature', 'properties': {}, 'geometry': {'type': 'Polygon', 'coordinates': [[[-92.8125, 17.308688], [-92.8125, 54.162434], [-18.984375, 54.162434], [-18.984375, 17.308688], [-92.8125, 17.308688]]]}}
#
# # Insert the document
# result = shapes.insert_one(geojson_data)
# print(f"Inserted document with ID: {result.inserted_id}")
# st.sidebar.header("Map")
# st.title("Geofence Feature")

st.markdown("""
<style>
    .maps-container {
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

st.markdown('<div class="main-column">', unsafe_allow_html=True)

map_col, output_col = st.columns([2, 1])

with map_col:
    with st.container():
        st.markdown("### Map")
        map_width = min(800, st.session_state.get('screen_width', 725))
        st_data = st_folium.st_folium(m, width=None, height=500, key="maps")

with output_col:
    # st.markdown("### Controls & Information")

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
                    else:
                        st.warning("Please enter a name!")
            with col2:
                if st.button("Skip", use_container_width=True):
                    save_properties(False, latest_drawing)

    st.subheader("Drawn Shapes Database")
    if st.session_state.named_shapes:
        for idx, shape in enumerate(st.session_state.named_shapes):
            shape_type = shape.get('geometry', {}).get('type', 'Unknown')
            shape_name = shape.get('properties', {}).get('name', 'Unnamed')

            with st.container():
                data, buttons = st.columns([1, 1])
                with data:
                    with st.expander(f"{idx + 1}. {shape_name} ({shape_type})", expanded=False):
                        st.json(shape.get('properties'), expanded=True)
                with buttons:
                    s_b, d_b = st.columns([1, 1])
                    with s_b:
                        st.button("Show",type="primary", key=f"{idx + 1}_show_button", use_container_width=True)
                    with d_b:
                        with d_b:
                            if st.button("Delete", key=f"{idx + 1}_del_button", use_container_width=True):
                                shapes.delete_one({'geometry': shape.get('geometry')})
                                st.session_state.named_shapes.pop(idx)
                                st.markdown(
                                    """
                                    <script>
                                        window.location.reload();
                                    </script>
                                    """,
                                    unsafe_allow_html=True
                                )
                                st.stop()


    else:
        st.info("No shapes drawn yet. Draw a shape on the maps to get started!")

    # with st.expander("Raw All Drawings Data"):
    #     st.code(str(all_drawings), language='json')
    #
    # with st.expander("Last Active Drawing"):
    #     st.code(str(st_data.get('last_active_drawing')), language='json')

st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)