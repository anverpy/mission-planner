import math
import random


class Weather:
    """
    A class to represent weather conditions.

    This class stores information about current weather conditions
    and provides methods to calculate the impact of weather on flight speed.

    Attributes:
        wind_speed (float): Wind speed in km/h.
        wind_direction (float): Wind direction in degrees.
        temperature (float): Temperature in degrees Celsius.
        humidity (float): Relative humidity in percent.
        pressure (float): Atmospheric pressure in hPa.
        description (str): Textual description of the weather.
    """

    def __init__(
        self,
        wind_speed: float,
        wind_direction: float,
        temperature: float,
        humidity: float,
        pressure: float,
        description: str,
    ):
        """
        Initialize a Weather instance.

        Args:
            wind_speed (float): Wind speed in km/h.
            wind_direction (float): Wind direction in degrees.
            temperature (float): Temperature in degrees Celsius.
            humidity (float): Relative humidity in percent.
            pressure (float): Atmospheric pressure in hPa.
            description (str): Textual description of the weather.
        """
        self.wind_speed = wind_speed
        self.wind_direction = wind_direction
        self.temperature = temperature
        self.humidity = humidity
        self.pressure = pressure
        self.description = description

    def __str__(self) -> str:
        return (
            f"Wind Speed: {self.wind_speed:.2f} km/h\n"
            f"Wind Direction: {self.wind_direction:.2f}°\n"
            f"Temperature: {self.temperature:.2f}°C\n"
            f"Humidity: {self.humidity}%\n"
            f"Pressure: {self.pressure} hPa\n"
            f"Description: {self.description}"
        )

    def impact_on_speed(self, flight_direction: float) -> float:
        """
        Calculate the impact of wind on flight speed.

        Args:
            flight_direction (float): The flight direction in degrees.

        Returns:
            float: The impact on speed in km/h (positive for tailwind, negative for headwind).
        """
        wind_dir_rad = math.radians(self.wind_direction)
        flight_dir_rad = math.radians(flight_direction)
        angle_diff = abs(wind_dir_rad - flight_dir_rad)
        wind_component = self.wind_speed * math.cos(angle_diff)
        return wind_component

    @classmethod
    def from_api(cls, api, lat: float, lon: float) -> "Weather":
        """
        Create a Weather instance from API data.

        Args:
            api (WeatherAPI): Instance of the weather API.
            lat (float): Latitude of the point.
            lon (float): Longitude of the point.

        Returns:
            Weather: A new Weather instance with API data.
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
    def generate_random(cls) -> "Weather":
        """
        Generate a Weather instance with random data.

        Returns:
            Weather: A new Weather instance with random data.
        """
        return cls(
            wind_speed=random.uniform(0, 100),
            wind_direction=random.uniform(0, 360),
            temperature=random.uniform(-10, 40),
            humidity=random.uniform(0, 100),
            pressure=random.uniform(950, 1050),
            description=random.choice(["Clear", "Cloudy", "Rainy", "Snowy", "Windy"]),
        )
