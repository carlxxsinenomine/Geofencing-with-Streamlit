# Windy API docs
# https://api.windy.com/point-forecast/docs

# TenDay
# https://tenday.pagasa.dost.gov.ph/docs

# Open-meteo
# https://open-meteo.com/

import requests
import os
from dotenv import load_dotenv
from web_scaper.PanahonScraper import PanahonScraper

load_dotenv()

WEATHER_API = os.getenv("WEATHER_API")
WINDY_API = os.getenv("WINDY_API")

class WeatherHandler:
    def __init__(self):
        # self.open_meteo_base = 'https://api.open-meteo.com/v1/forecast'
        self.weatherapi_base_alert =  'http://api.weatherapi.com/v1/alerts.json'
        self.weatherapi_base_forecast = 'http://api.weatherapi.com/v1/forecast.json'
        self.weatherapi_base_current_forecast = 'http://api.weatherapi.com/v1/current.json'
        self.weatherapi_base_search = 'http://api.weatherapi.com/v1/search.json'

        self.windy_api_base = "https://api.windy.com/api/point-forecast/v2"

    def get_panahon_advisory(self, location):
        panahon = PanahonScraper()
        panahon.start_scraping(location=location)
        return panahon.get_data()

    #
    #
    # def get_marine_forecast(self):
    #     pass

    """
    For weather api
    """
    def get_current_forecast(self, lat=13.539201, lng=118.696289):
        params = {
            'key': WEATHER_API,
            'q': f"{13.143245},{123.741798}"  # Format: "latitude,longitude"
        }
        try:
            response = requests.get(self.weatherapi_base_current_forecast, params=params)
            response.raise_for_status()
            return (response.json())['current']

        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            return None

    def get_coordinates_info(self, lat= 14.103029, long=122.932497):
        params = {
            'key': WEATHER_API,
            'q': f"{lat},{long}"  # Format: "latitude,longitude"
        }

        try:
            response = requests.get(self.weatherapi_base_current_forecast, params=params)
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
