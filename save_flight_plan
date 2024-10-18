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
    Una clase para representar un plan de vuelo con consideraciones meteorológicas.

    Esta clase proporciona métodos para calcular rutas, distancias y tiempos de vuelo estimados
    teniendo en cuenta las condiciones meteorológicas actuales.

    Atributos:
        departure (tuple): Coordenadas (lat, lon) del punto de partida.
        arrival (tuple): Coordenadas (lat, lon) del punto de llegada.
        waypoints (list): Lista de tuplas de coordenadas para puntos intermedios.
        weather_conditions (dict): Condiciones meteorológicas almacenadas en caché para coordenadas.
        total_distance (float): Distancia total de la ruta de vuelo en km.
        adjusted_speed (float): Velocidad ajustada considerando las condiciones meteorológicas.
        weather_api (WeatherAPI): Instancia de WeatherAPI para obtener datos meteorológicos.
    """

    def __init__(self, departure, arrival, waypoints=[]):
        """
        Inicializa una instancia de FlightPlan.

        Args:
            departure (tuple): Coordenadas (lat, lon) del punto de partida.
            arrival (tuple): Coordenadas (lat, lon) del punto de llegada.
            waypoints (list, opcional): Lista de tuplas de coordenadas para puntos intermedios.
            api_key (str, opcional): Clave API para datos meteorológicos. Por defecto es None.
        """
        self.departure = self._validate_coordinates(departure)
        self.arrival = self._validate_coordinates(arrival)
        self.waypoints = [self._validate_coordinates(wp) for wp in waypoints]
        self.weather_conditions = {}
        self.total_distance = 0
        self.adjusted_speed = 0
        self.weather_api = WeatherAPI()

    def __repr__(self):
        """
        Devuelve una representación en cadena del objeto FlightPlan.

        Esta representación incluye los puntos de partida, llegada y los puntos intermedios del plan de vuelo.

        Returns:
            str: Una cadena que representa el objeto FlightPlan.
        """
        return f"FlightPlan(departure={self.departure}, arrival={self.arrival}, waypoints={self.waypoints})"

    def _validate_coordinates(self, coord):
        """
        Valida las coordenadas dadas.

        Verifica que las coordenadas sean flotantes, tengan 4 decimales y estén dentro de los rangos válidos de latitud y longitud.

        Args:
            coord (tuple): Una tupla con la latitud y longitud a validar.

        Returns:
            tuple: Las coordenadas validadas.

        Raises:
            ValueError: Si las coordenadas no cumplen con los criterios de validación.
        """
        lat, lon = coord
        if not (isinstance(lat, float) and isinstance(lon, float)):
            raise ValueError(
                f"Coordinates must be float type. Given coordinate: {coord}"
            )
        if len(str(lat).split(".")[1]) != 4 or len(str(lon).split(".")[1]) != 4:
            raise ValueError(
                f"Coordinates must have 4 decimal places. Given coordinate: {coord}"
            )
        if not (-90 <= lat <= 90):
            raise ValueError(
                f"Latitude {lat} is not valid. Must be between -90 and 90."
            )
        if not (-180 <= lon <= 180):
            raise ValueError(
                f"Longitude {lon} is not valid. Must be between -180 and 180."
            )
        return coord

    @contextmanager
    def weather_api_context(self):
        """
        Administrador de contexto para operaciones con la API del clima.

        Proporciona un contexto seguro para realizar operaciones con la API del clima,
        manejando posibles errores y asegurando una correcta gestión de recursos.

        Yields:
            WeatherAPI or None: La instancia de WeatherAPI si está disponible, None en caso contrario.
        """
        if self.weather_api is None:
            yield None
        else:
            try:
                yield self.weather_api
            except Exception as e:
                print(f"Error accessing weather API: {e}")
                yield None

    def get_weather_at_point(self, coordinates):
        """
        Obtiene las condiciones meteorológicas para las coordenadas dadas.

        Este método obtiene datos meteorológicos de la API si está disponible, de lo contrario
        genera datos meteorológicos aleatorios. Los resultados se almacenan en caché para eficiencia.

        Args:
            coordinates (tuple): Latitud y longitud del punto.

        Returns:
            Weather: Una instancia de la clase Weather con las condiciones actuales.
        """
        if coordinates not in self.weather_conditions:
            with self.weather_api_context() as api:
                if api:
                    try:
                        weather_data = api.get_weather(*coordinates)
                        self.weather_conditions[coordinates] = Weather(**weather_data)
                    except Exception as e:
                        print(f"Error obtaining weather data for {coordinates}: {e}")
                        self.weather_conditions[coordinates] = (
                            self._generate_random_weather()
                        )
                else:
                    self.weather_conditions[coordinates] = (
                        self._generate_random_weather()
                    )
        return self.weather_conditions[coordinates]

    def _generate_random_weather(self):
        """
        Genera datos meteorológicos aleatorios.

        Este método se utiliza cuando no se puede acceder a la API del clima para obtener datos reales.

        Returns:
            Weather: Una instancia de Weather con datos meteorológicos generados aleatoriamente.
        """
        return Weather(
            wind_speed=random.uniform(0, 100),
            wind_direction=random.uniform(0, 360),
            temperature=random.uniform(-10, 40),
            humidity=random.uniform(0, 100),
            pressure=random.uniform(950, 1050),
            description=random.choice(["Clear", "Cloudy", "Rainy", "Snowy", "Windy"]),
        )

    def calculate_route(self):
        """
        Calcula la distancia total de la ruta y obtiene las condiciones meteorológicas.

        Este método calcula la distancia total de la ruta de vuelo, incluyendo
        los puntos intermedios, y obtiene datos meteorológicos para los puntos de partida y llegada.

        Returns:
            float: La distancia total de la ruta en kilómetros.
        """
        total_distance = 0
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

    def _get_point_name(self, coordinates):
        """
        Obtiene el nombre de un punto basado en sus coordenadas.

        Args:
            coordinates (tuple): Una tupla con la latitud y longitud del punto.

        Returns:
            str: El nombre del punto si está en la lista predefinida, o una representación de las coordenadas.
        """
        point_names = {
            (40.4168, -3.7038): "Madrid",
            (41.6528, -4.7245): "Valladolid",
            (40.9429, -4.1088): "Segovia",
        }
        return point_names.get(coordinates, f"Point {coordinates}")

    @staticmethod
    @lru_cache(maxsize=None)
    def haversine_distance(coord1, coord2):
        """
        Calcula la distancia del círculo máximo entre dos puntos en la Tierra usando la fórmula del haversine.

        Este método está decorado con @lru_cache para mejorar el rendimiento en cálculos repetidos.

        Args:
            coord1 (tuple): Coordenadas (latitud, longitud) del primer punto.
            coord2 (tuple): Coordenadas (latitud, longitud) del segundo punto.

        Returns:
            float: La distancia entre los dos puntos en kilómetros.
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

    def calculate_flight_direction(self):
        """
        Calcula la dirección inicial del vuelo desde el punto de partida hasta el punto de llegada.

        Utiliza la fórmula del rumbo inicial para determinar la dirección del vuelo en grados.

        Returns:
            float: La dirección del vuelo en grados (0-360).
        """
        lat1, lon1 = math.radians(self.departure[0]), math.radians(self.departure[1])
        lat2, lon2 = math.radians(self.arrival[0]), math.radians(self.arrival[1])

        dlon = lon2 - lon1

        y = math.sin(dlon) * math.cos(lat2)
        x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(
            lat2
        ) * math.cos(dlon)

        initial_bearing = math.atan2(y, x)

        initial_bearing = math.degrees(initial_bearing)
        compass_bearing = (initial_bearing + 360) % 360

        return compass_bearing

    def estimate_time(self, cruise_speed):
        """
        Estima el tiempo de vuelo considerando las condiciones meteorológicas.

        Este método calcula el tiempo de vuelo estimado basado en la velocidad de crucero dada,
        ajustando por las condiciones de viento e incluyendo tiempo para las fases de
        taxi, ascenso y descenso.

        Args:
            cruise_speed (float): La velocidad de crucero de la aeronave en km/h.

        Returns:
            float: Tiempo total de vuelo estimado en horas.

        Raises:
            ValueError: Si la velocidad de crucero proporcionada no es positiva.
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

        climb_descent_distance = (climb_time + descent_time) * (
            adjusted_cruise_speed / 2
        )
        cruise_distance = max(0, self.total_distance - climb_descent_distance)
        cruise_time = cruise_distance / adjusted_cruise_speed

        total_time = taxi_time + climb_time + cruise_time + descent_time

        self.adjusted_speed = self.total_distance / total_time  # Actual average speed

        return total_time


if __name__ == "__main__":
    try:
        api_key = os.getenv("API_KEY")
        weather_api = WeatherAPI()

        if weather_api.check_api_status():
            print("\nWeather API is working correctly")
        else:
            print("\nWeather API is not working correctly")
            api_key = None  # This will force the use of random weather data

        madrid = (40.4168, -3.7038)
        valladolid = (41.6528, -4.7245)
        segovia = (40.9429, -4.1088)

        flight_plan = FlightPlan(madrid, valladolid, [segovia])

        total_distance = flight_plan.calculate_route()
        estimated_time = flight_plan.estimate_time(800)

        print(f"\nTotal distance: {total_distance:.2f} km")
        print(f"Average speed: {flight_plan.adjusted_speed:.2f} km/h")
        print(
            f"Estimated flight time: {estimated_time:.2f} hours ({estimated_time*60:.0f} minutes)\n"
        )

    except ValueError as e:
        print(f"Error: {e}")
