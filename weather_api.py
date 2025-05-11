import os
import requests
import os
from dotenv import load_dotenv

class WeatherAPI:
    """
    A class to interact with the OpenWeatherMap API.

    This class provides methods to obtain current weather data
    for specific geographic coordinates.

    Attributes:
        api_key (str): The API key for accessing OpenWeatherMap.
        base_url (str): The base URL for API requests.
    """

    def __init__(self):
        """
        Initialize WeatherAPI with the provided API key.
        """
        load_dotenv()  # Loads variables from .env file
        self.api_key = os.getenv("API_KEY")
        # No lanzar error, simplemente establecer api_key como None
        # para que se puedan usar datos simulados
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"

    def get_weather(self, lat: float, lon: float) -> dict:
        """
        Get current weather data for the given latitude and longitude.

        Args:
            lat (float): Latitude of the location.
            lon (float): Longitude of the location.

        Returns:
            dict: A dictionary with weather data, including wind speed,
                  wind direction, temperature, humidity, pressure, and description.

        Raises:
            Exception: If there is an error obtaining weather data.
        """
        # Si no hay API key configurada, lanzar una excepción que será capturada
        # por el FlightPlan para usar datos simulados
        if not self.api_key:
            raise Exception("No API key provided")
            
        params = {"lat": lat, "lon": lon, "appid": self.api_key, "units": "metric"}
        response = requests.get(self.base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            return {
                "wind_speed": data["wind"]["speed"],
                "wind_direction": data["wind"]["deg"],
                "temperature": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "description": data["weather"][0]["description"],
            }
        else:
            raise Exception(f"Error fetching weather data: {response.status_code}")

    def check_api_status(self) -> bool:
        """
        Check if the API is working correctly.

        Returns:
            bool: True if the API is working, False otherwise.
        """
        try:
            self.get_weather(51.5074, -0.1278)  # London coordinates
            return True
        except Exception:
            return False
