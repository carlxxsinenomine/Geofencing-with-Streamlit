import folium
import requests
import streamlit as st
import streamlit_folium
import streamlit_folium as st_folium
from folium import JsCode
from folium.plugins import Realtime


m = folium.Map(location=[0, 0], zoom_start=12)

rt = folium.plugins.LocateControl(auto_start=True).add_to(m)
st.write(rt.to_dict())

st_data = st_folium.st_folium(m, width=725)