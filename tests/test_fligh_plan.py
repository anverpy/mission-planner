"""
Unit test module for the FlightPlan class.

This module contains unit tests to verify the correct operation
of the FlightPlan class and its associated methods. The tests
cover initialization, coordinate validation, weather data retrieval,
route calculation, and flight time estimation.
"""

import unittest
from unittest.mock import patch, MagicMock
from flight_plan import FlightPlan
from weather import Weather

class TestFlightPlan(unittest.TestCase):
    """
    Test suite for the FlightPlan class.

    This class contains test methods to verify the correct behavior
    of the different components of the FlightPlan class.
    """

    def setUp(self) -> None:
        """
        Set up the test environment before each test method.

        Initializes the departure, arrival, and waypoint coordinates
        to be used in the tests.
        """
        self.departure = (40.4168, -3.7038)  # Madrid
        self.arrival = (41.6528, -4.7245)  # Valladolid
        self.waypoint = (40.9429, -4.1088)  # Segovia

    def test_init(self):
        """
        Test correct initialization of a FlightPlan object.

        Verifies that the departure, arrival, and waypoint attributes
        are set correctly during initialization.
        """
        fp = FlightPlan(self.departure, self.arrival, [self.waypoint])
        self.assertEqual(fp.departure, self.departure)
        self.assertEqual(fp.arrival, self.arrival)
        self.assertEqual(fp.waypoints, [self.waypoint])

    def test_validate_coordinates(self):
        """
        Test coordinate validation.

        Verifies that the _validate_coordinates method accepts valid coordinates
        and rejects invalid ones, raising a ValueError.
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
        Test weather data retrieval for a point.

        Uses a mock WeatherAPI to simulate weather data retrieval
        and verifies that a Weather object is correctly created.
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

        fp = FlightPlan(self.departure, self.arrival)
        weather = fp.get_weather_at_point(self.departure)

        self.assertIsInstance(weather, Weather)
        self.assertEqual(weather.wind_speed, 10)
        self.assertEqual(weather.description, "Cloudy")

    def test_calculate_route(self):
        """
        Test flight route calculation.

        Verifies that the calculate_route method returns a total distance
        greater than zero for a valid route.
        """
        fp = FlightPlan(self.departure, self.arrival, [self.waypoint])
        total_distance = fp.calculate_route()
        self.assertGreater(total_distance, 0)

    def test_estimate_time(self):
        """
        Test flight time estimation.

        Simulates weather conditions and verifies that the estimated time
        is reasonable for a given distance and speed.
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
