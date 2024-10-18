"""
Módulo de pruebas unitarias para la clase FlightPlan.

Este módulo contiene pruebas unitarias para verificar el funcionamiento
correcto de la clase FlightPlan y sus métodos asociados. Las pruebas
cubren la inicialización, validación de coordenadas, obtención de datos
meteorológicos, cálculo de rutas y estimación de tiempos de vuelo.
"""

import set_pythonpath
import unittest
from unittest.mock import patch, MagicMock
from flight_plan import FlightPlan, Coordinate
from weather import Weather


class TestFlightPlan(unittest.TestCase):
    """
    Conjunto de pruebas para la clase FlightPlan.

    Esta clase contiene métodos de prueba para verificar el comportamiento
    correcto de los diferentes componentes de la clase FlightPlan.
    """

    def setUp(self):
        """
        Configura el entorno de prueba antes de cada método de prueba.

        Inicializa las coordenadas de partida, llegada y punto intermedio
        que se utilizarán en las pruebas.
        """
        self.departure = (40.4168, -3.7038)  # Madrid
        self.arrival = (41.6528, -4.7245)  # Valladolid
        self.waypoint = (40.9429, -4.1088)  # Segovia

    def test_init(self):
        """
        Prueba la inicialización correcta de un objeto FlightPlan.

        Verifica que los atributos de partida, llegada y puntos intermedios
        se establezcan correctamente durante la inicialización.
        """
        fp = FlightPlan(self.departure, self.arrival, [self.waypoint])
        self.assertEqual(fp.departure, self.departure)
        self.assertEqual(fp.arrival, self.arrival)
        self.assertEqual(fp.waypoints, [self.waypoint])

    def test_validate_coordinates(self):
        """
        Prueba la validación de coordenadas.

        Verifica que el método _validate_coordinates acepte coordenadas válidas
        y rechace las inválidas, lanzando una excepción ValueError.
        """
        fp = FlightPlan(self.departure, self.arrival)
        valid_coord = (40.4168, -3.7038)
        invalid_coord = (91.0000, 181.0000)

        self.assertEqual(fp._validate_coordinates(valid_coord), valid_coord)
        with self.assertRaises(ValueError):
            fp._validate_coordinates(invalid_coord)

    @patch("flight_plan.WeatherAPI")
    def test_get_weather_at_point(self, mock_weather_api):
        """
        Prueba la obtención de datos meteorológicos para un punto.

        Utiliza un mock de WeatherAPI para simular la obtención de datos
        meteorológicos y verifica que se cree correctamente un objeto Weather.
        """
        mock_api_instance = MagicMock()
        mock_weather_api.return_value = mock_api_instance
        mock_api_instance.get_weather.return_value = {
            "wind_speed": 10,
            "wind_direction": 180,
            "temperature": 20,
            "humidity": 50,
            "pressure": 1013,
            "description": "Cloudy",
        }

        fp = FlightPlan(self.departure, self.arrival, api_key="test_key")
        weather = fp.get_weather_at_point(self.departure)

        self.assertIsInstance(weather, Weather)
        self.assertEqual(weather.wind_speed, 10)
        self.assertEqual(weather.description, "Cloudy")

    def test_calculate_route(self):
        """
        Prueba el cálculo de la ruta de vuelo.

        Verifica que el método calculate_route devuelva una distancia total
        mayor que cero para una ruta válida.
        """
        fp = FlightPlan(self.departure, self.arrival, [self.waypoint])
        total_distance = fp.calculate_route()

        # You might want to calculate the expected distance separately
        # and compare it with a small tolerance
        self.assertGreater(total_distance, 0)

    def test_estimate_time(self):
        """
        Prueba la estimación del tiempo de vuelo.

        Simula condiciones meteorológicas y verifica que el tiempo estimado
        sea razonable para una distancia y velocidad dadas.
        """
        fp = FlightPlan(self.departure, self.arrival)
        fp.total_distance = 100  # Set a known distance for testing

        with patch.object(fp, "get_weather_at_point") as mock_get_weather:
            mock_get_weather.return_value = Weather(10, 0, 20, 50, 1013, "Clear")
            estimated_time = fp.estimate_time(800)

        self.assertGreater(estimated_time, 0)
        self.assertLess(estimated_time, 1)  # Should take less than an hour at 800 km/h


if __name__ == "__main__":
    unittest.main()
