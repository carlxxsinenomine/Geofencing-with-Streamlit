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

m = folium.Map(zoom_start=12)

# Draw plugin for drawing shapes on map layer
# set polyline, and circlemarker to false since nde naman need
Draw(
    export=False,
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
    st_data = st_folium.st_folium(m, width=725)
with output_col:
    st.write(st_data)