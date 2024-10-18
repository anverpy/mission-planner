import math
import random


class Weather:
    """
    Una clase para representar las condiciones meteorológicas.

    Esta clase almacena información sobre las condiciones meteorológicas actuales
    y proporciona métodos para calcular el impacto del clima en la velocidad de vuelo.

    Atributos:
        wind_speed (float): Velocidad del viento en km/h.
        wind_direction (float): Dirección del viento en grados.
        temperature (float): Temperatura en grados Celsius.
        humidity (float): Humedad relativa en porcentaje.
        pressure (float): Presión atmosférica en hPa.
        description (str): Descripción textual del clima.
    """

    def __init__(
        self, wind_speed, wind_direction, temperature, humidity, pressure, description
    ):
        """
        Inicializa una instancia de Weather.

        Args:
            wind_speed (float): Velocidad del viento en km/h.
            wind_direction (float): Dirección del viento en grados.
            temperature (float): Temperatura en grados Celsius.
            humidity (float): Humedad relativa en porcentaje.
            pressure (float): Presión atmosférica en hPa.
            description (str): Descripción textual del clima.
        """

        self.wind_speed = wind_speed
        self.wind_direction = wind_direction
        self.temperature = temperature
        self.humidity = humidity
        self.pressure = pressure
        self.description = description

    def __str__(self):
        return (
            f"Wind Speed: {self.wind_speed:.2f} km/h\n"
            f"Wind Direction: {self.wind_direction:.2f}°\n"
            f"Temperature: {self.temperature:.2f}°C\n"
            f"Humidity: {self.humidity}%\n"
            f"Pressure: {self.pressure} hPa\n"
            f"Description: {self.description}"
        )

    def impact_on_speed(self, flight_direction):
        """
        Calcula el impacto del viento en la velocidad de vuelo.

        Args:
            flight_direction (float): La dirección del vuelo en grados.

        Returns:
            float: El impacto en la velocidad en km/h (positivo para viento a favor, negativo para viento en contra).
        """
        wind_dir_rad = math.radians(self.wind_direction)
        flight_dir_rad = math.radians(flight_direction)
        angle_diff = abs(wind_dir_rad - flight_dir_rad)
        wind_component = self.wind_speed * math.cos(angle_diff)
        return wind_component

    @classmethod
    def from_api(cls, api, lat, lon):
        """
        Crea una instancia de Weather a partir de datos de la API.

        Args:
            api (WeatherAPI): Instancia de la API del clima.
            lat (float): Latitud del punto.
            lon (float): Longitud del punto.

        Returns:
            Weather: Una nueva instancia de Weather con datos de la API.
        """

        weather_data = api.get_weather(lat, lon)
        return cls(
            weather_data["wind_speed"],
            weather_data["wind_direction"],
            weather_data["temperature"],
            weather_data["humidity"],
            weather_data["pressure"],
            weather_data["description"],
        )

    @classmethod
    def generate_random(cls):
        """
        Genera una instancia de Weather con datos aleatorios.

        Returns:
            Weather: Una nueva instancia de Weather con datos aleatorios.
        """
        return cls(
            wind_speed=random.uniform(0, 100),
            wind_direction=random.uniform(0, 360),
            temperature=random.uniform(-10, 40),
            humidity=random.uniform(0, 100),
            pressure=random.uniform(950, 1050),
            description=random.choice(["Clear", "Cloudy", "Rainy", "Snowy", "Windy"]),
        )
