import requests
from dotenv import load_dotenv
from pathlib import Path
import os

# Get parent directory 
env_path = Path(__file__).resolve().parent.parent.parent / '.env'

# Load .env from parent directory
load_dotenv(dotenv_path=env_path)
# api_key = os.getenv("api_key")
# api_url = f"http://api.weatherstack.com/current?access_key={api_key}&query=New York"

# def fetch_data():
#     try:
#         print(f"Fetching weather result")
#         print(api_key)
#         response = requests.get(api_url)
#         response.raise_for_status()
#         print(f"Response fetched successfully", response.json())
#         print(f"Response fetched successfully", response)
#         return response.json()
#     except requests.exceptions.RequestException as e:
#         print(f"Error while fetching data: {e}")
#         raise

# fetch_data()  

def mock_fetch_data():
    return {'request': {'type': 'City', 'query': 'New York, United States of America', 'language': 'en', 'unit': 'm'}, 'location': {'name': 'New York', 'country': 'United States of America', 'region': 'New York', 'lat': '40.714', 'lon': 
'-74.006', 'timezone_id': 'America/New_York', 'localtime': '2025-06-06 15:13', 'localtime_epoch': 1749222780, 'utc_offset': '-4.0'}, 'current': {'observation_time': '07:13 PM', 'temperature': 28, 'weather_code': 113, 'weather_icons': ['https://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0001_sunny.png'], 'weather_descriptions': ['Sunny'], 'astro': {'sunrise': '05:26 AM', 'sunset': '08:24 PM', 'moonrise': '04:16 PM', 'moonset': '02:32 AM', 'moon_phase': 'Waxing Gibbous', 'moon_illumination': 
76}, 'air_quality': {'co': '440.3', 'no2': '40.885', 'o3': '77', 'so2': '7.03', 'pm2_5': '24.975', 'pm10': '28.305', 'us-epa-index': '2', 'gb-defra-index': '2'}, 'wind_speed': 20, 'wind_degree': 164, 'wind_dir': 'SSE', 'pressure': 1013, 'precip': 0, 'humidity': 55, 'cloudcover': 0, 'feelslike': 29, 'uv_index': 4, 'visibility': 11, 'is_day': 'yes'}}
      
