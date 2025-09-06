import requests
import json
from datetime import datetime
import os
from .help import get_current_timestamp_gmt7

class WeatherAPI:
    def __init__(self, api_key="d4c99fc363a241e0d1d2bf886e4d231b", base_url="http://api.openweathermap.org/data/2.5"):
        self.api_key = api_key
        self.base_url = base_url
    
    def get_weather_data(self, city_name):
        try:
            url = f"{self.base_url}/weather"
            params = {
                'q': city_name,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'data': {
                        'temperature': data['main']['temp'],
                        'humidity': data['main']['humidity'],
                        'city': city_name,
                        'timestamp': get_current_timestamp_gmt7()
                    },
                    'status_code': response.status_code
                }
            else:
                return {
                    'success': False,
                    'status_code': response.status_code,
                    'message': response.text
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'status_code': 500,
                'message': f"Request error: {str(e)}"
            }
        except KeyError as e:
            return {
                'success': False,
                'status_code': 500,
                'message': f"Data parsing error: {str(e)}"
            }
    
    def save_to_json(self, data, filename="data_weather.json"):
        try:
            log_dir = "log"
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            filepath = os.path.join(log_dir, filename)
            
            existing_data = []
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    try:
                        existing_data = json.load(f)
                    except json.JSONDecodeError:
                        existing_data = []
            
            existing_data.append(data)
 
            with open(filepath, 'w') as f:
                json.dump(existing_data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving to JSON: {e}")
            return False