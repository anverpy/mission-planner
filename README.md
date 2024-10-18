# Mission Planner 🛩

MissionPlanner es una aplicación de planificación de vuelos que calcula rutas y tiempos estimados considerando condiciones meteorológicas en tiempo real. Utiliza la API de OpenWeatherMap para obtener datos meteorológicos precisos.

## Características ✓

- Cálculo de rutas de vuelo entre puntos de partida y llegada
- Consideración de waypoints intermedios
- Obtención de datos meteorológicos en tiempo real
- Ajuste de velocidad y tiempo de vuelo basado en condiciones de viento
- Cálculo de distancias utilizando la fórmula del haversine


## Instalación ⚙

1. Clona este repositorio:
git clone [https://github.com/anverpy/mission-planner.git](https://github.com/anverpy/mission-planner.git)

2. Instala dependencias
   pip install -r requirements.txt
   
3. Crea un archivo `.env` en la raíz del proyecto y añade tu API key de OpenWeatherMap:
   API_KEY=tu_api_key_aquí
   

## Uso ⏯

Para ejecutar la aplicación, usa el siguiente comando:
python flight_plan.py


El script calculará una ruta de vuelo de ejemplo entre Madrid y Valladolid, pasando por Segovia, y mostrará las condiciones meteorológicas, la distancia total, la velocidad media y el tiempo estimado de vuelo.

## Estructura del proyecto 🏗

- `flight_plan.py`: Contiene la clase principal `FlightPlan` que maneja la lógica de planificación de vuelos.
- `weather.py`: Define la clase `Weather` para representar y manejar datos meteorológicos.
- `weather_api.py`: Implementa la clase `WeatherAPI` para interactuar con la API de OpenWeatherMap.
- `.env`: Archivo para almacenar la API key (no incluido en el repositorio).
- `.gitignore`: Especifica los archivos que Git debe ignorar.
- `requirements.txt`: Lista las dependencias del proyecto.

## Configuración ⚙

Asegúrate de tener un archivo `.env` en la raíz del proyecto con tu API key de OpenWeatherMap:


## Contribuir 📪

Las contribuciones son bienvenidas. Por favor, abre un issue para discutir cambios mayores antes de hacer un pull request.

1. Haz fork del proyecto
2. Crea tu rama de características (`git checkout -b feature/AmazingFeature`)
3. Haz commit de tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia ■

Distribuido bajo la Licencia MIT. Ver `LICENSE` para más información.

## Contacto ✉

Andrés Vergara - andresw206@gmail.com

Link del Proyecto: [https://github.com/anverpy/mission-planner.git](https://github.com/anverpy/mission-planner.git)
