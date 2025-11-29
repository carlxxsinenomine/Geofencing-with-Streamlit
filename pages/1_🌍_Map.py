import folium
import pymongo
import streamlit as st
import streamlit_folium as st_folium

from folium.plugins import Draw, Fullscreen

# Initialize geocoder
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from map.gps_tracking_control import GPSTrackingControl

st.set_page_config(
    page_title="Map",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"  # Changed to show sidebar by default
)

# Initialize session state for view toggle
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = 'shapes'  # 'shapes' or 'chat'

# Initialize API key in session state
if 'gemini_api_key' not in st.session_state:
    st.session_state.gemini_api_key = ""

# Sidebar toggle
with st.sidebar:
    st.title("View Options")

    view_option = st.radio(
        "Select View:",
        options=['shapes', 'chat'],
        format_func=lambda x: '📊 Drawn Shapes Database' if x == 'shapes' else '💬 Chat with AI',
        key='view_toggle'
    )

    st.session_state.view_mode = view_option

    # Show API key input only when Chat is selected
    if view_option == 'chat':
        st.markdown("---")
        st.subheader("🔑 API Configuration")

        api_key = st.text_input(
            "Gemini API Key:",
            value=st.session_state.gemini_api_key,
            type="password",
            placeholder="Enter your Google Gemini API key",
            help="Get your free API key from https://ai.google.dev/"
        )

        if api_key != st.session_state.gemini_api_key:
            st.session_state.gemini_api_key = api_key

        if st.session_state.gemini_api_key:
            st.success("✅ API key configured")
        else:
            st.warning("⚠️ Please enter your API key to use the chatbot")

    st.markdown("---")
    st.caption("Toggle between database view and chat interface")

m = folium.Map(
    zoom_start=5,
    location=[13.00000000, 122.00000000],
    max_zoom=22,
    min_zoom=3
)

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
    client = pymongo.MongoClient(
        st.secrets["mongo"],
        tlsAllowInvalidCertificates=True
    )
    geo_db = client.geospatial_data
    return {'shapes_collection': geo_db.shapes,
            'user_collection': geo_db.user,
            'trail_collection': geo_db.user_trail}


db_collections = init_connection()
shapes = db_collections['shapes_collection']
trail_collection = db_collections['trail_collection']

if 'named_shapes' not in st.session_state:
    try:
        st.session_state.named_shapes = [
            {'type': shape['type'],
             'properties': shape['properties'],
             'geometry': shape['geometry']}
            for shape in shapes.find()
        ]
    except Exception as e:
        st.info("There are no Drawn shapes on map")
        st.session_state.named_shapes = []

if 'pending_name' not in st.session_state:
    st.session_state.pending_name = False
if 'processed_shape_ids' not in st.session_state:
    st.session_state.processed_shape_ids = set()

# Chat history initialization
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []


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

folium.TileLayer(
    tiles='https://api.mapbox.com/styles/v1/mapbox/streets-v11/tiles/{z}/{x}/{y}?access_token=pk.eyJ1IjoiY2FybHh4IiwiYSI6ImNtaTlzY3VzcTBvYXcyaXB4NGw4ZnFkOW4ifQ.edIRnWcs645EJxC0oJ1NNw',
    attr='Mapbox',
    name='Mapbox Streets',
    overlay=False,
    control=True
).add_to(m)

folium.TileLayer(
    tiles='https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
    attr='OpenTopoMap',
    name='OpenTopoMap',
    overlay=False,
    control=True
).add_to(m)

folium.TileLayer('CartoDB dark_matter', name='Dark Mode').add_to(m)

folium.LayerControl().add_to(m)

Fullscreen(
    position='topright',
    title='Expand me bitch',
    title_cancel='Exit kana?',
    force_separate_button=True
).add_to(m)

st.markdown("""
<style>
    .maps-container {
        position: relative;
        width: 100%;
        height: 60vh;
        min-height: 400px;
    }

    @media (max-width: 768px) {
        .main-column {
            flex-direction: column;
        }
        .stColumn {
            min-width: 100% !important;
        }
    }

    .mobile-button {
        width: 100%;
        margin: 5px 0;
    }

    .responsive-text {
        font-size: calc(14px + 0.5vw);
    }

    /* Chat UI Styling - Dark Theme */
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border: 1px solid #2a2a2a;
    }

    .chat-message.user {
        background-color: #1e3a5f;
        border-left: 4px solid #2196f3;
        color: #e3f2fd;
    }

    .chat-message.assistant {
        background-color: #1a1a1a;
        border-left: 4px solid #4caf50;
        color: #e0e0e0;
    }

    .chat-header {
        font-weight: bold;
        margin-bottom: 0.5rem;
        color: #ffffff;
    }

    /* Chat container background */
    .chat-container {
        background-color: #0d1117;
        padding: 1rem;
        border-radius: 0.5rem;
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

    # Show name input dialog if pending (always show this regardless of view mode)
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

            st.markdown("---")

    # Conditional rendering based on view mode
    if st.session_state.view_mode == 'shapes':
        # DRAWN SHAPES DATABASE VIEW
        st.subheader("📊 Drawn Shapes Database")
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
                            st.button("Show", type="primary", key=f"{idx + 1}_show_button", use_container_width=True)
                        with d_b:
                            if st.button("Delete", key=f"{idx + 1}_del_button", use_container_width=True):
                                try:
                                    shapes.delete_one({'geometry': shape.get('geometry')})
                                    st.session_state.named_shapes.pop(idx)
                                    shape_id = shape.get('properties', {}).get('shape_id')
                                    if shape_id and shape_id in st.session_state.processed_shape_ids:
                                        st.session_state.processed_shape_ids.discard(shape_id)
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error deleting shape: {e}")
        else:
            st.info("No shapes drawn yet. Draw a shape on the map to get started!")

    else:
        # CHAT UI VIEW
        st.subheader("💬 Disaster Risk Chatbot")
        st.caption("Ask questions about disaster preparedness and risk reduction")

        # Chat container with scrollable area
        chat_container = st.container()

        with chat_container:
            # Display chat history
            for message in st.session_state.chat_history:
                role = message['role']
                content = message['content']

                if role == 'user':
                    st.markdown(f"""
                    <div class="chat-message user">
                        <div class="chat-header">👤 You</div>
                        <div>{content}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message assistant">
                        <div class="chat-header">🤖 Assistant</div>
                        <div>{content}</div>
                    </div>
                    """, unsafe_allow_html=True)

        # Chat input at the bottom
        st.markdown("---")

        with st.form(key='chat_form', clear_on_submit=True):
            user_input = st.text_input(
                "Ask a question:",
                placeholder="e.g., What should I do during an earthquake?",
                label_visibility="collapsed"
            )

            col1, col2 = st.columns([3, 1])
            with col1:
                submit_button = st.form_submit_button("Send", type="primary", use_container_width=True)
            with col2:
                clear_button = st.form_submit_button("Clear", use_container_width=True)

        if submit_button and user_input:
            # Check if API key is configured
            if not st.session_state.gemini_api_key:
                st.error("❌ Please configure your Gemini API key in the sidebar first!")
                st.stop()

            # Add user message to history
            st.session_state.chat_history.append({
                'role': 'user',
                'content': user_input
            })

            # Connect to your RAG chatbot
            try:
                from chatbot.rag_pipeline import DisasterChatbot

                # Use absolute path to chroma_db
                import os
                import sys
                from pathlib import Path

                # Get the project root directory (where your Home_Page.py is located)
                project_root = Path(__file__).parent.parent  # Go up two levels from pages/map.py

                # Database is in the root's chatbot/chroma_db
                chroma_db_path = project_root / "chatbot" / "chroma_db"

                # Add debug info
                # st.write(f"🔍 Project root: {project_root}")
                # st.write(f"🔍 Database path: {chroma_db_path}")
                # st.write(f"🔍 Database exists: {chroma_db_path.exists()}")

                chatbot = DisasterChatbot(
                    db_dir=str(chroma_db_path),  # Convert to string
                    gemini_api_key=st.session_state.gemini_api_key
                )

                response = chatbot.ask(user_input, return_sources=False)
                bot_response = response['answer']

            except Exception as e:
                import traceback

                error_details = traceback.format_exc()
                st.error(f"Detailed error: {error_details}")
                bot_response = f"❌ Error: {str(e)}\n\nPlease check your API key and database configuration."

            # Add bot response to history
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': bot_response
            })

            st.rerun()

        if clear_button:
            st.session_state.chat_history = []
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)