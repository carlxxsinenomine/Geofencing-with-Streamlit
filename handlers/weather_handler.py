# Windy API docs
# https://api.windy.com/point-forecast/docs

# TenDay
# https://tenday.pagasa.dost.gov.ph/docs

# Open-meteo
# https://open-meteo.com/

import requests
import os
from dotenv import load_dotenv

load_dotenv()

WEATHER_API = os.getenv("WEATHER_API")


class WeatherHandler:
    def __init__(self):
        self.open_meteo_base = 'https://api.open-meteo.com/v1/forecast'
        self.weatherapi_base_alert =  'http://api.weatherapi.com/v1/alerts.json'
        self.weatherapi_base_forecast = 'http://api.weatherapi.com/v1/forecast.json'
        self.weatherapi_base_search = 'http://api.weatherapi.com/v1/search.json'

    """
    For open-meteo
    """
    def get_weather_forecast(self, long, lat):
        weather_params = {
            'latitude': lat,
            'longitude': long,
            'hourly': [],
            'daily': [],
            'forecast_days': 7,
            'timezone': 'auto'
        }

    def get_marine_forecast(self):
        pass



    """
    For weather api
    """
    def get_forecast(self):
        pass

    def get_forecast_alert(self):
        params = {
            'key': WEATHER_API,
            'q': f"{13.143245},{123.741798}"  # Format: "latitude,longitude"
        }
        try:
            response = requests.get(self.weatherapi_base_alert, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            return None

    def get_user_info(self):
        url = "http://api.weatherapi.com/v1/current.json"
        params = {
            'key': WEATHER_API,
            'q': f"{13.143245},{123.741798}"  # Format: "latitude,longitude"
        }

        try:
            response = requests.get(url, params=params)
            data = response.json()

            location = data['location']
            return {
                'name': location['name'],
                'region': location['region'],  # This is the state/province
                'country': location['country'],
                'state_province': location['region'],  # Alias for clarity
                'timezone': location['tz_id'],
                'lat': location['lat'],
                'lon': location['lon']
            }
        except Exception as e:
            print(f"Error: {e}")
            return None

w = WeatherHandler()
print(w.get_forecast_alert())