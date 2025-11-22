import geopandas as gpd
import requests

# Example: Download from WMS/WFS service
wfs_url = "https://hazard-api.dream.upd.edu.ph/geoserver/wfs"

params = {
    'service': 'WFS',
    'version': '2.0.0',
    'request': 'GetFeature',
    'typeName': 'dream:flood_hazard',  # Check actual layer name
    'outputFormat': 'json'
}

response = requests.get(wfs_url, params=params)
gdf = gpd.read_file(response.text)