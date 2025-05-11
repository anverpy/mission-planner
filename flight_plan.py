import math
import random
import os
from weather import Weather
from weather_api import WeatherAPI
from functools import lru_cache
from collections import namedtuple
from contextlib import contextmanager

Coordinate = namedtuple("Coordinate", ["lat", "lon"])

class FlightPlan:
    """
    A class to represent a flight plan with weather considerations.

    This class provides methods to calculate routes, distances, and estimated flight times
    taking into account current weather conditions.

    Attributes:
        departure (tuple): Coordinates (lat, lon) of the departure point.
        arrival (tuple): Coordinates (lat, lon) of the arrival point.
        waypoints (list): List of coordinate tuples for intermediate points.
        weather_conditions (dict): Cached weather conditions for coordinates.
        total_distance (float): Total route distance in km.
        adjusted_speed (float): Speed adjusted for weather conditions.
        weather_api (WeatherAPI): Instance of WeatherAPI to obtain weather data.
    """

    def __init__(self, departure: tuple, arrival: tuple, waypoints: list = []):
        """
        Initialize a FlightPlan instance.

        Args:
            departure (tuple): Coordinates (lat, lon) of the departure point.
            arrival (tuple): Coordinates (lat, lon) of the arrival point.
            waypoints (list, optional): List of coordinate tuples for intermediate points.
        """
        self.departure = self._validate_coordinates(departure)
        self.arrival = self._validate_coordinates(arrival)
        self.waypoints = [self._validate_coordinates(wp) for wp in waypoints]
        self.weather_conditions = {}
        self.total_distance = 0.0
        self.adjusted_speed = 0.0
        self.weather_api = WeatherAPI()

    def __repr__(self) -> str:
        """
        Return a string representation of the FlightPlan object.

        Returns:
            str: A string representing the FlightPlan object.
        """
        return f"FlightPlan(departure={self.departure}, arrival={self.arrival}, waypoints={self.waypoints})"

    def _validate_coordinates(self, coord: tuple) -> tuple:
        """
        Validate the given coordinates.

        Checks that the coordinates are floats, have 4 decimal places, and are within valid latitude and longitude ranges.

        Args:
            coord (tuple): A tuple with latitude and longitude to validate.

        Returns:
            tuple: The validated coordinates.

        Raises:
            ValueError: If the coordinates do not meet validation criteria.
        """
        lat, lon = coord
        if not (isinstance(lat, float) and isinstance(lon, float)):
            raise ValueError(f"Coordinates must be float type. Given coordinate: {coord}")
        if len(str(lat).split(".")[1]) != 4 or len(str(lon).split(".")[1]) != 4:
            raise ValueError(f"Coordinates must have 4 decimal places. Given coordinate: {coord}")
        if not (-90 <= lat <= 90):
            raise ValueError(f"Latitude {lat} is not valid. Must be between -90 and 90.")
        if not (-180 <= lon <= 180):
            raise ValueError(f"Longitude {lon} is not valid. Must be between -180 and 180.")
        return coord

    @contextmanager
    def weather_api_context(self):
        """
        Context manager for weather API operations.

        Provides a safe context for weather API operations, handling possible errors and ensuring proper resource management.

        Yields:
            WeatherAPI or None: The WeatherAPI instance if available, None otherwise.
        """
        if self.weather_api is None:
            yield None
        else:
            try:
                yield self.weather_api
            except Exception as e:
                print(f"Error accessing weather API: {e}")
                yield None

    def get_weather_at_point(self, coordinates: tuple) -> Weather:
        """
        Get weather conditions for the given coordinates.

        This method obtains weather data from the API if available, otherwise
        generates random weather data. Results are cached for efficiency.

        Args:
            coordinates (tuple): Latitude and longitude of the point.

        Returns:
            Weather: An instance of the Weather class with current conditions.
        """
        if coordinates not in self.weather_conditions:
            with self.weather_api_context() as api:
                if api:
                    try:
                        weather_data = api.get_weather(*coordinates)
                        self.weather_conditions[coordinates] = Weather(**weather_data)
                    except Exception as e:
                        print(f"Error obtaining weather data for {coordinates}: {e}")
                        self.weather_conditions[coordinates] = self._generate_random_weather()
                else:
                    self.weather_conditions[coordinates] = self._generate_random_weather()
        return self.weather_conditions[coordinates]

    def _generate_random_weather(self) -> Weather:
        """
        Generate random weather data.

        This method is used when the weather API is not accessible to obtain real data.

        Returns:
            Weather: An instance of Weather with randomly generated weather data.
        """
        return Weather(
            wind_speed=random.uniform(0, 100),
            wind_direction=random.uniform(0, 360),
            temperature=random.uniform(-10, 40),
            humidity=random.uniform(0, 100),
            pressure=random.uniform(950, 1050),
            description=random.choice(["Clear", "Cloudy", "Rainy", "Snowy", "Windy"]),
        )

    def calculate_route(self) -> float:
        """
        Calculate the total route distance and get weather conditions.

        This method calculates the total distance of the flight route, including
        intermediate waypoints, and obtains weather data for the departure and arrival points.

        Returns:
            float: The total route distance in kilometers.
        """
        total_distance = 0.0
        route = [self.departure] + self.waypoints + [self.arrival]

        for i in range(len(route) - 1):
            distance = self.haversine_distance(route[i], route[i + 1])
            total_distance += distance

        self.total_distance = total_distance

        # Get and display weather for departure and arrival
        departure_weather = self.get_weather_at_point(self.departure)
        arrival_weather = self.get_weather_at_point(self.arrival)

        print("\nWeather conditions:\n")
        print(f"Departure ({self._get_point_name(self.departure)}):")
        print(departure_weather)
        print(f"\nArrival ({self._get_point_name(self.arrival)}):")
        print(arrival_weather)

        return total_distance

    def _get_point_name(self, coordinates: tuple) -> str:
        """
        Get the name of a point based on its coordinates.

        Args:
            coordinates (tuple): A tuple with the latitude and longitude of the point.

        Returns:
            str: The name of the point if it is in the predefined list, or a representation of the coordinates.
        """
        point_names = {
            (40.4168, -3.7038): "Madrid",
            (41.6528, -4.7245): "Valladolid",
            (40.9429, -4.1088): "Segovia",
        }
        return point_names.get(coordinates, f"Point {coordinates}")

    @staticmethod
    @lru_cache(maxsize=None)
    def haversine_distance(coord1: tuple, coord2: tuple) -> float:
        """
        Calculate the great-circle distance between two points on Earth using the haversine formula.

        This method is decorated with @lru_cache to improve performance on repeated calculations.

        Args:
            coord1 (tuple): Coordinates (latitude, longitude) of the first point.
            coord2 (tuple): Coordinates (latitude, longitude) of the second point.

        Returns:
            float: The distance between the two points in kilometers.
        """
        R = 6371  # Earth's radius in kilometers

        lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
        lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    def calculate_flight_direction(self) -> float:
        """
        Calculate the initial flight direction from the departure point to the arrival point.

        Uses the initial bearing formula to determine the flight direction in degrees.

        Returns:
            float: The flight direction in degrees (0-360).
        """
        lat1, lon1 = math.radians(self.departure[0]), math.radians(self.departure[1])
        lat2, lon2 = math.radians(self.arrival[0]), math.radians(self.arrival[1])

        dlon = lon2 - lon1

        y = math.sin(dlon) * math.cos(lat2)
        x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)

        initial_bearing = math.atan2(y, x)
        initial_bearing = math.degrees(initial_bearing)
        compass_bearing = (initial_bearing + 360) % 360

        return compass_bearing

    def estimate_time(self, cruise_speed: float) -> float:
        """
        Estimate the flight time considering weather conditions.

        This method calculates the estimated flight time based on the given cruise speed,
        adjusting for wind conditions and including time for taxi, climb, and descent phases.

        Args:
            cruise_speed (float): The aircraft's cruise speed in km/h.

        Returns:
            float: Estimated total flight time in hours.

        Raises:
            ValueError: If the provided cruise speed is not positive.
        """
        if cruise_speed <= 0:
            raise ValueError("Speed must be greater than 0.")

        weather_at_departure = self.get_weather_at_point(self.departure)
        flight_direction = self.calculate_flight_direction()

        wind_impact = weather_at_departure.impact_on_speed(flight_direction)
        adjusted_cruise_speed = max(100, cruise_speed + wind_impact)

        taxi_time = 10 / 60  # 10 minutes in hours
        climb_time = 15 / 60  # 15 minutes in hours
        descent_time = 15 / 60  # 15 minutes in hours

        climb_descent_distance = (climb_time + descent_time) * (adjusted_cruise_speed / 2)
        cruise_distance = max(0, self.total_distance - climb_descent_distance)
        cruise_time = cruise_distance / adjusted_cruise_speed

        total_time = taxi_time + climb_time + cruise_time + descent_time

        self.adjusted_speed = self.total_distance / total_time  # Actual average speed

        return total_time
