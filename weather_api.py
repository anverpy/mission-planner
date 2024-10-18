import os
import requests
from dotenv import load_dotenv


class WeatherAPI:
    """
    Una clase para interactuar con la API de OpenWeatherMap.

    Esta clase proporciona métodos para obtener datos meteorológicos actuales
    para coordenadas geográficas específicas.

    Atributos:
        api_key (str): La clave API para acceder a OpenWeatherMap.
        base_url (str): La URL base para las solicitudes a la API.
    """

    def __init__(self):
        """
        Inicializa la WeatherAPI con la clave API proporcionada.

        Args:
            api_key (str): La clave API para acceder a OpenWeatherMap.
        """
        load_dotenv()  # Esto carga las variables del archivo .env
        self.api_key = os.getenv("API_KEY")
        if not self.api_key:
            raise ValueError("API_KEY no está configurada en el archivo .env")
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"

    def get_weather(self, lat: float, lon: float):
        """
        Obtiene datos meteorológicos actuales para la latitud y longitud dadas.

        Args:
            lat (float): La latitud de la ubicación.
            lon (float): La longitud de la ubicación.

        Returns:
            dict: Un diccionario con los datos meteorológicos, incluyendo velocidad del viento,
                  dirección del viento, temperatura, humedad, presión y descripción.

        Raises:
            Exception: Si hay un error al obtener los datos meteorológicos.
        """
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

    def check_api_status(self):
        """
        Verifica si la API está funcionando correctamente.

        Returns:
            bool: True si la API está funcionando, False en caso contrario.
        """
        try:
            self.get_weather(51.5074, -0.1278)  # London coordinates
            return True
        except Exception:
            return False
