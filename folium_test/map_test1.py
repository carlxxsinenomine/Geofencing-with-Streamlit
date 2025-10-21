import folium
import requests
import streamlit as st
import streamlit_folium
import streamlit_folium as st_folium
from folium import JsCode
from folium.plugins import Realtime
from folium.plugins import Draw


m = folium.Map(location=[0, 0], zoom_start=12)
draw = Draw(export=True).add_to(m)

st.set_page_config(layout="wide")

rt = folium.plugins.LocateControl(auto_start=True).add_to(m)

map_col, output_col = st.columns(2)

with map_col:
    st_data = st_folium.st_folium(m, width=725)
with output_col:
    st.write(st_data)