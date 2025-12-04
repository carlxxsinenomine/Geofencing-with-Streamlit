# Windy API docs
# https://api.windy.com/point-forecast/docs

# TenDay
# https://tenday.pagasa.dost.gov.ph/docs

# Open-meteo
# https://open-meteo.com/

import requests
import os
from dotenv import load_dotenv
from typing import Optional, Dict

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

    def get_panahon_advisory(self, location: str) -> Dict:
        """
        Fetch weather alerts from the Flask API endpoint instead of scraping directly.

        Args:
            location: Location name to fetch weather alerts for (e.g., "Naga", "Masbate")

        Returns:
            Dictionary containing weather alerts or None values if failed
        """
        try:
            # API endpoint
            api_url = "https://flask-server-production-c983.up.railway.app/get-weather-alerts"

            print(f"🌐 Fetching weather alerts for: {location}")

            # Make GET request with location parameter
            response = requests.get(
                api_url,
                params={"location": location},
                timeout=220  # 2 minute timeout since scraping takes time
            )

            print(f"📡 Response status: {response.status_code}")

            # Check if request was successful
            response.raise_for_status()

            # Parse JSON response
            data = response.json()

            print(f"📦 Response data: {data}")

            if data.get("success"):
                alerts = data.get("alerts", {
                    'Rainfall': None,
                    'Thunderstorm': None,
                    'Flood': None,
                    'Tropical': None
                })
                print(f"✅ Successfully retrieved alerts: {alerts}")
                return alerts
            else:
                error_msg = data.get('error', 'Unknown error')
                print(f"❌ API returned error: {error_msg}")
                return {
                    'Rainfall': None,
                    'Thunderstorm': None,
                    'Flood': None,
                    'Tropical': None
                }

        except requests.exceptions.Timeout:
            error_msg = f"⏱️ Request timeout while fetching weather alerts for {location}"
            print(error_msg)
            return {
                'Rainfall': None,
                'Thunderstorm': None,
                'Flood': None,
                'Tropical': None
            }

        except requests.exceptions.RequestException as e:
            error_msg = f"❌ Error fetching weather alerts from API: {e}"
            print(error_msg)
            return {
                'Rainfall': None,
                'Thunderstorm': None,
                'Flood': None,
                'Tropical': None
            }

        except Exception as e:
            error_msg = f"❌ Unexpected error: {e}"
            print(error_msg)
            import traceback
            return {
                'Rainfall': None,
                'Thunderstorm': None,
                'Flood': None,
                'Tropical': None
            }

    #
    #
    # def get_marine_forecast(self):
    #     pass

    """
    For weather api
    """

    def get_current_forecast(self, lat=13.147298, lng= 123.731476):
        params = {
            'key': WEATHER_API,
            'q': f"{lat},{lng}"
        }
        try:
            response = requests.get(self.weatherapi_base_current_forecast, params=params)
            response.raise_for_status()
            data = response.json()

            # Check if 'current' key exists
            if 'current' not in data:
                print(f"Warning: 'current' key not found in response: {data}")
                return None

            return data['current']

        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            return None
        except KeyError as e:
            print(f"Data parsing error: {e}")
            return None

    def get_coordinates_info(self, lat=13.147298, long= 123.731476):
        params = {
            'key': WEATHER_API,
            'q': f"{lat},{long}"
        }

        try:
            response = requests.get(self.weatherapi_base_current_forecast, params=params)
            response.raise_for_status()  # ✅ Add this to catch HTTP errors
            data = response.json()

            # Check if location exists
            if 'location' not in data:
                print(f"Warning: 'location' key not found in response")
                return None

            location = data['location']
            return {
                'name': location.get('name', 'Unknown'),
                'region': location.get('region', 'Unknown'),
                'country': location.get('country', 'Unknown'),
                'state_province': location.get('region', 'Unknown'),
                'timezone': location.get('tz_id', 'Unknown'),
                'lat': location.get('lat', lat),
                'lon': location.get('lon', long)
            }
        except Exception as e:
            print(f"Error: {e}")
            return None