import streamlit as st
from weather import Weather
from weather_api import WeatherAPI
from flight_plan import FlightPlan
import folium
from streamlit_folium import st_folium
import numpy as np
import datetime
import pandas as pd
from io import BytesIO
import time
import base64
import altair as alt

# Set page configuration and theme
st.set_page_config(
    page_title="Flight Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state variables
if 'origin' not in st.session_state:
    st.session_state['origin'] = None
if 'destination' not in st.session_state:
    st.session_state['destination'] = None
if 'aircraft' not in st.session_state:
    st.session_state['aircraft'] = "Cessna 172"
if 'cruise_speed' not in st.session_state:
    st.session_state['cruise_speed'] = 226  # Default Cessna 172 speed
if 'route_history' not in st.session_state:
    st.session_state['route_history'] = []  # List to store history of routes
if 'show_history' not in st.session_state:
    st.session_state['show_history'] = False  # Toggle for history sidebar

# Custom CSS to enhance the visual appearance
st.markdown("""
<style>    /* Main app styling */
    .main .block-container {
        padding-top: 0.75rem;
        padding-bottom: 2rem;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #3B82F6;
    }
    
    /* Title adjustment */
    h1:first-of-type {
        margin-top: 0;
        padding-top: 0;
        margin-bottom: 0.5rem;
    }
    
    /* Info boxes */
    .info-box {
        background-color: rgba(30, 41, 59, 0.7);
        border-left: 4px solid #3B82F6;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        color: #e2e8f0;
    }
    
    /* Success box */
    .success-box {
        background-color: rgba(20, 83, 45, 0.7);
        border-left: 4px solid #22c55e;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.5rem;
        color: #e2e8f0;
    }
    
    /* Warning box */
    .warning-box {
        background-color: rgba(113, 63, 18, 0.7);
        border-left: 4px solid #f59e0b;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.5rem;
        color: #e2e8f0;
    }
    
    /* Custom metric card */
    .metric-card {
        background-color: rgba(30, 41, 59, 0.7);
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
        transition: all 0.3s;
        color: #e2e8f0;
    }
    
    .metric-card:hover {
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.4);
        transform: translateY(-2px);
    }
    
    .metric-value {
        font-size: 1.5rem;
        font-weight: bold;
        color: #60a5fa;
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: #94a3b8;
        margin-top: 0.25rem;
    }
    
    /* Styling for the selection boxes */
    .selection-box {
        border: 1px solid #4b5563;
        border-radius: 5px;
        padding: 15px;
        background-color: rgba(30, 41, 59, 0.7);
        margin-bottom: 20px;
        color: #e2e8f0;
    }
    .selection-title {
        font-weight: bold;
        margin-bottom: 10px;
        color: #60a5fa;
    }
    .selection-item {
        margin-bottom: 5px;
        color: #e2e8f0;
    }
      /* Flight details styling */
    .flight-info {
        background-color: rgba(30, 58, 87, 0.7);
        border-radius: 10px;
        padding: 15px;
        margin: 20px 0;
        color: #e2e8f0;
    }
    .flight-route {
        font-size: 1.2em;
        font-weight: bold;
        color: #60a5fa;
        margin-bottom: 15px;
    }
    .flight-detail {
        margin-bottom: 8px;
        color: #e2e8f0;
    }
    
    /* Download button styling */
    .download-btn {
        display: inline-block;
        padding: 8px 16px;
        background-color: #2563eb;
        color: white;
        text-decoration: none;
        border-radius: 4px;
        font-weight: bold;
        margin: 10px 0;
        text-align: center;
        transition: all 0.3s;
    }
    .download-btn:hover {
        background-color: #3b82f6;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.3);
    }
</style>
""", unsafe_allow_html=True)

CITY_COORDS = {
    "Valladolid": (41.6528, -4.7244),
    "León": (42.5987, -5.5671),
    "Madrid": (40.4168, -3.7038),
    "Sevilla": (37.3886, -5.9823),
    "Gijón": (43.5453, -5.6615),
    "Cádiz": (36.5271, -6.2886),
    "Barcelona": (41.3874, 2.1686)
}

CITY_COLORS = {
    "Valladolid": "purple",
    "León": "darkred",
    "Madrid": "black",
    "Sevilla": "green",
    "Gijón": "lightblue",
    "Cádiz": "orange",
    "Barcelona": "cadetblue"
}

# Aircraft data dictionary
AIRCRAFT_DATA = {
    "Cessna 172": {"cruise_speed": 226, "range": 1289, "ceiling": 14000, "fuel_consumption": 36},
    "Cirrus SR22": {"cruise_speed": 300, "range": 1600, "ceiling": 17500, "fuel_consumption": 60},
    "Piper PA-28": {"cruise_speed": 235, "range": 1100, "ceiling": 14000, "fuel_consumption": 40},
    "Diamond DA40": {"cruise_speed": 280, "range": 1400, "ceiling": 16400, "fuel_consumption": 33},
    "Beechcraft Bonanza": {"cruise_speed": 320, "range": 1800, "ceiling": 18500, "fuel_consumption": 68},
    "Airbus A320": {"cruise_speed": 840, "range": 6100, "ceiling": 39000, "fuel_consumption": 2500}
}

# App header layout - Title and history button on same line
header_col1, header_col2 = st.columns([11, 1])

with header_col1:
    st.title("✈️ Flight Planner Dashboard")

with header_col2:
    # Button to toggle history sidebar
    if st.button("📜" if not st.session_state['show_history'] else "✖️", key="history_toggle"):
        st.session_state['show_history'] = not st.session_state['show_history']
        st.rerun()

# Show sidebar with history if enabled
if st.session_state['show_history']:
    with st.sidebar:
        st.title("Recent Routes")
        
        # Add custom CSS for the sidebar history items
        st.markdown("""
        <style>
        .history-item {
            background-color: rgba(30, 41, 59, 0.7);
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 15px;
            border-left: 4px solid #3b82f6;
        }
        .history-route {
            font-size: 1.1em;
            font-weight: bold;
            color: #60a5fa;
            margin-bottom: 10px;
        }
        .history-detail {
            font-size: 0.9em;
            color: #cbd5e1;
            margin-bottom: 3px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        if len(st.session_state['route_history']) == 0:
            st.info("No recent routes. Plan a flight to see your history.")
        else:
            for i, route in enumerate(st.session_state['route_history']):
                with st.container():
                    st.markdown(f"""
                    <div class="history-item">
                        <div class="history-route">{i+1}. {route['origin']} → {route['destination']}</div>
                        <div class="history-detail">🕒 {route['timestamp']}</div>
                        <div class="history-detail">✈️ {route['aircraft']}</div>
                        <div class="history-detail">📏 {route['distance']:.1f} km</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("Load Route", key=f"load_route_{i}", use_container_width=True):
                        st.session_state['origin'] = route['origin']
                        st.session_state['destination'] = route['destination']
                        st.session_state['aircraft'] = route['aircraft']
                        st.rerun()

# App description with improved styling
st.markdown("""
    <div class="info-box" style="margin-top: 0.5rem;">
        <h4 style="margin-top:0; margin-bottom: 0.5rem;">Welcome to Flight Planner</h4>
        <p style="margin-bottom: 0.25rem;">Plan your flight by selecting origin and destination cities on the interactive map. 
        Get detailed weather information, route details, and flight recommendations.</p>
    </div>
""", unsafe_allow_html=True)

# Progress tracker based on selections
progress_status = 0
progress_text = "Step 1: Select origin city"

if st.session_state['origin']:
    progress_status = 50
    progress_text = "Step 2: Select destination city"
    
if st.session_state['origin'] and st.session_state['destination']:
    progress_status = 100
    progress_text = "Flight plan complete! Explore the details below."

# Show progress bar
st.progress(progress_status/100)
st.caption(progress_text)

# Function to add a route to history
def add_route_to_history(origin, destination, distance, aircraft):
    """Add a route to the history, maintaining only the last 5 routes"""
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    new_route = {
        "timestamp": timestamp,
        "origin": origin,
        "destination": destination,
        "distance": distance,
        "aircraft": aircraft
    }
    
    # Add to beginning of list (most recent first)
    st.session_state['route_history'].insert(0, new_route)
    
    # Keep only the last 5 routes
    if len(st.session_state['route_history']) > 5:
        st.session_state['route_history'] = st.session_state['route_history'][:5]

# Build the map
m = folium.Map(location=[40.4168, -3.7038], zoom_start=6)

# Add city markers
for city, coords in CITY_COORDS.items():
    color = CITY_COLORS[city]
    
    # Determinamos si este punto es origen o destino
    is_origin = st.session_state['origin'] == city
    is_destination = st.session_state['destination'] == city
    
    # Para resaltar visualmente pero mantener el color original, usamos un icono más grande si es origen o destino
    icon_size = None
    if is_origin:
        # Agregar un círculo verde debajo del marcador para indicar origen
        folium.CircleMarker(
            coords,
            radius=15,
            color='green',
            fill=True,
            fill_opacity=0.3,
            popup=None
        ).add_to(m)
    elif is_destination:
        # Agregar un círculo rojo debajo del marcador para indicar destino
        folium.CircleMarker(
            coords,
            radius=15,
            color='red',
            fill=True,
            fill_opacity=0.3,
            popup=None
        ).add_to(m)
    
    # Siempre añadir el marcador con su color original
    folium.Marker(
        coords,
        tooltip=city,
        icon=folium.Icon(color=color),
        popup=city
    ).add_to(m)

# Draw route if both selected
if st.session_state['origin'] and st.session_state['destination']:
    folium.PolyLine([
        CITY_COORDS[st.session_state['origin']],
        CITY_COORDS[st.session_state['destination']]
    ], color="purple", weight=3, opacity=0.8).add_to(m)

# Mostrar el mapa en toda la anchura de la pantalla
map_data = st_folium(m, width="100%", height=500, returned_objects=["last_object_clicked_popup"])

# Handle marker click for selection
clicked = map_data.get("last_object_clicked_popup") if 'map_data' in locals() else None
if clicked:
    city_clicked = clicked
    if not st.session_state['origin']:
        st.session_state['origin'] = city_clicked
        st.rerun()
    elif not st.session_state['destination'] and city_clicked != st.session_state['origin']:
        st.session_state['destination'] = city_clicked
        st.rerun()

# Organizar los controles de configuración en columnas debajo del mapa
left_config_col, right_config_col = st.columns([1, 1])

# Columna izquierda - Configuración de ruta
with left_config_col:
    # 1. Flight Route Selection Section
    st.markdown("""
        <div class="selection-box">
            <div class="selection-title">📍 Flight Route</div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        origin_status = st.session_state['origin'] or "Select on map"
        origin_color = "green" if st.session_state['origin'] else "gray"
        st.markdown(f"""
            <div style="border-left: 4px solid {origin_color}; padding-left: 10px;">
                <b>Origin:</b><br>{origin_status}
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        dest_status = st.session_state['destination'] or "Select on map"
        dest_color = "red" if st.session_state['destination'] else "gray"
        st.markdown(f"""
            <div style="border-left: 4px solid {dest_color}; padding-left: 10px;">
                <b>Destination:</b><br>{dest_status}
            </div>
        """, unsafe_allow_html=True)
    
    if st.button("🔄 Reset Selection", use_container_width=True):
        st.session_state['origin'] = None
        st.session_state['destination'] = None
        st.rerun()

# Columna derecha - Configuración de aeronave y parámetros
with right_config_col:
    # 2. Aircraft Selection & Configuration
    st.markdown("""
        <div class="selection-box">
            <div class="selection-title">🛩️ Aircraft Configuration</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Aircraft selector
    selected_aircraft = st.selectbox(
        "Select Aircraft Model",
        options=list(AIRCRAFT_DATA.keys()),
        index=list(AIRCRAFT_DATA.keys()).index(st.session_state['aircraft']),
        key="aircraft_selector"
    )
    
    # Update session state if aircraft changed
    if selected_aircraft != st.session_state['aircraft']:
        st.session_state['aircraft'] = selected_aircraft
        st.session_state['cruise_speed'] = AIRCRAFT_DATA[selected_aircraft]['cruise_speed']
        if st.session_state['origin'] and st.session_state['destination']:
            st.rerun()
    
    # Aircraft info display
    st.markdown(f"""        <div style="background-color: rgba(30, 41, 59, 0.7); border-radius: 5px; padding: 10px; margin-top: 10px; color: #e2e8f0;">
            <div style="display: flex; justify-content: space-between;">
                <span><b>Cruise Speed:</b> {AIRCRAFT_DATA[selected_aircraft]['cruise_speed']} km/h</span>
                <span><b>Range:</b> {AIRCRAFT_DATA[selected_aircraft]['range']} km</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-top: 5px;">
                <span><b>Ceiling:</b> {AIRCRAFT_DATA[selected_aircraft]['ceiling']} ft</span>
                <span><b>Fuel Usage:</b> {AIRCRAFT_DATA[selected_aircraft]['fuel_consumption']} {selected_aircraft == "Airbus A320" and 'kg/h' or 'L/h'}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # 3. Flight Parameters
    st.markdown("""
        <div class="selection-box" style="margin-top: 20px;">
            <div class="selection-title">⚙️ Flight Parameters</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Speed adjustment slider
    default_speed = AIRCRAFT_DATA[st.session_state['aircraft']]['cruise_speed']
    min_speed = int(default_speed * 0.7)
    max_speed = int(default_speed * 1.2)
    
    adjusted_speed = st.slider(
        "Cruise Speed (km/h)",
        min_value=min_speed,
        max_value=max_speed,
        value=st.session_state['cruise_speed'],
        step=5
    )
    
    # Update session state if speed changed
    if adjusted_speed != st.session_state['cruise_speed']:
        st.session_state['cruise_speed'] = adjusted_speed
        if st.session_state['origin'] and st.session_state['destination']:
            st.rerun()

# Si se ha seleccionado origen y destino, mostrar detalles del vuelo
if st.session_state['origin'] and st.session_state['destination']:
    # Separador visual 
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Cabecera de detalles de vuelo
    st.header("Flight Details")
    
    # Obtener datos del vuelo
    dep = CITY_COORDS[st.session_state['origin']]
    arr = CITY_COORDS[st.session_state['destination']]
    flight_plan = FlightPlan(dep, arr, [])
    total_distance = flight_plan.calculate_route()
    
    # Use the selected cruise speed
    selected_speed = st.session_state['cruise_speed']
    estimated_time = flight_plan.estimate_time(selected_speed)
    
    # Calculate fuel consumption
    aircraft = st.session_state['aircraft']
    fuel_rate = AIRCRAFT_DATA[aircraft]['fuel_consumption']  # L/h
    total_fuel = fuel_rate * estimated_time  # Total fuel in liters
    
    # Check if this is a different route from the most recent one in history
    # If so, add it to history
    if (len(st.session_state['route_history']) == 0 or 
        st.session_state['route_history'][0]['origin'] != st.session_state['origin'] or
        st.session_state['route_history'][0]['destination'] != st.session_state['destination'] or
        st.session_state['route_history'][0]['aircraft'] != aircraft):
        add_route_to_history(
            st.session_state['origin'],
            st.session_state['destination'],
            total_distance,
            aircraft
        )
    
    # Resumen de ruta
    st.success(f"{st.session_state['origin']} → {st.session_state['destination']}")
    
    # Mostrar métricas del vuelo en tres columnas
    metric_col1, metric_col2, metric_col3 = st.columns(3)
    with metric_col1:
        st.metric("Distance", f"{total_distance:.1f} km")
        st.metric("Cruise Speed", f"{selected_speed} km/h")
    
    with metric_col2:
        hours = int(estimated_time)
        minutes = int((estimated_time - hours) * 60)
        st.metric("Flight Time", f"{hours}h {minutes}m")
        
        aircraft_range = AIRCRAFT_DATA[aircraft]['range']
        range_status = "✅ OK" if total_distance <= aircraft_range else "⚠️ Exceeded"
        range_delta = f"{(aircraft_range - total_distance):.0f} km margin" if total_distance <= aircraft_range else None
        st.metric("Range", range_status, delta=range_delta)
        
    with metric_col3:
        # Ajuste de unidades para mostrar en L para aviones pequeños y kg para comerciales
        fuel_unit = "kg" if aircraft == "Airbus A320" else "L"
        fuel_value = total_fuel if aircraft != "Airbus A320" else total_fuel
        st.metric("Fuel Required", f"{fuel_value:.1f} {fuel_unit}")
        
        # Add fuel efficiency status
        if aircraft == "Diamond DA40":
            efficiency = "Excellent"
            delta_color = "off" 
        elif aircraft == "Airbus A320":
            efficiency = "Commercial"
            delta_color = "off"
        elif total_fuel < 50:
            efficiency = "Good"
            delta_color = "off"
        else:
            efficiency = "Moderate" 
            delta_color = "off"
        
        st.metric("Fuel Efficiency", efficiency)
    
    # Organizar información en pestañas
    info_tabs = st.tabs(["Weather", "Flight Recommendations", "Flight Planning", "Report"])
    
    # Get weather data
    dep_weather = flight_plan.get_weather_at_point(dep)
    arr_weather = flight_plan.get_weather_at_point(arr)
      # Pestaña de información meteorológica
    with info_tabs[0]:
        # Add data source indicator - check if we're using real API data
        api_active = hasattr(flight_plan, 'weather_api') and flight_plan.weather_api.api_key and flight_plan.weather_api.api_key.strip()
        data_source = "Real-time API data" if api_active else "Simulated weather data"
        source_color = "#22c55e" if api_active else "#f59e0b"  # Green if real, orange if simulated
        
        st.markdown(f"""
            <div style="background-color: rgba(30, 41, 59, 0.7); border-left: 4px solid {source_color}; 
                padding: 8px 15px; border-radius: 4px; margin-bottom: 20px; font-size: 0.9em; color: #e2e8f0;">
                <div style="display: flex; align-items: center;">
                    <span style="font-size: 1.2em; margin-right: 8px; color: {source_color};">{"✓" if api_active else "⚠"}</span>
                    <span><b>Data source:</b> {data_source}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Weather comparison in two columns
        weather_col1, weather_col2 = st.columns(2)
        
        # Departure weather
        with weather_col1:
            st.subheader(f"Departure: {st.session_state['origin']}")
            st.markdown(f"**Temperature:** {dep_weather.temperature}°C")
            st.markdown(f"**Conditions:** {dep_weather.description}")
            st.markdown(f"**Wind:** {dep_weather.wind_speed} km/h")
            st.markdown(f"**Humidity:** {dep_weather.humidity}%")
            st.markdown(f"**Pressure:** {dep_weather.pressure} hPa")
            if hasattr(dep_weather, 'visibility'):
                st.markdown(f"**Visibility:** {dep_weather.visibility/1000:.1f} km")        
        # Arrival weather
        with weather_col2:
            st.subheader(f"Arrival: {st.session_state['destination']}")
            st.markdown(f"**Temperature:** {arr_weather.temperature}°C")
            st.markdown(f"**Conditions:** {arr_weather.description}")
            st.markdown(f"**Wind:** {arr_weather.wind_speed} km/h")
            st.markdown(f"**Humidity:** {arr_weather.humidity}%")
            st.markdown(f"**Pressure:** {arr_weather.pressure} hPa")
            if hasattr(arr_weather, 'visibility'):
                st.markdown(f"**Visibility:** {arr_weather.visibility/1000:.1f} km")
    
    # Pestaña de recomendaciones de vuelo
    with info_tabs[1]:
        # Check aircraft range vs distance
        range_warning = ""
        if total_distance > AIRCRAFT_DATA[aircraft]['range']:
            range_warning = f"⚠️ Flight distance ({total_distance:.0f} km) exceeds {aircraft} range ({AIRCRAFT_DATA[aircraft]['range']} km). Consider refueling stops."
            st.warning(range_warning)
            
        # Weather warnings
        if dep_weather.wind_speed > 20 or arr_weather.wind_speed > 20:
            st.warning("⚠️ High winds detected. Consider adjusting flight path or time of departure.")
        elif "rain" in dep_weather.description.lower() or "rain" in arr_weather.description.lower():
            st.warning("⚠️ Rain conditions detected. Check for updates before departure.")
        else:
            st.success("✅ Weather conditions suitable for flight.")
            
        # Add information about optimal altitude based on weather and aircraft ceiling
        aircraft_ceiling = AIRCRAFT_DATA[aircraft]['ceiling']
        
        # Ajustar la altitud óptima según el tipo de aeronave
        if aircraft == "Airbus A320":
            optimal_altitude = min(aircraft_ceiling * 0.85, 35000)  # Los aviones comerciales vuelan más alto
        else:
            optimal_altitude = min(aircraft_ceiling * 0.7, 8000)  # Aeronaves pequeñas
        
        # Adjust for weather conditions
        if dep_weather.temperature < 10 or arr_weather.temperature < 10:
            # Para aviones comerciales y pequeños, ajustamos de manera diferente
            if aircraft == "Airbus A320":
                optimal_altitude = min(aircraft_ceiling * 0.9, 37000)
            else:
                optimal_altitude = min(aircraft_ceiling * 0.8, 10000)
        
        # Ajustar unidades para aviones comerciales
        fuel_unit = "kg" if aircraft == "Airbus A320" else "L"
        reserve_time = "45 min" if aircraft == "Airbus A320" else "30 min"
        
        # Mostrar recomendaciones
        st.subheader("Flight Recommendations")
        st.markdown(f"""
            - **Recommended cruise altitude:** {optimal_altitude:.0f} feet (Max ceiling: {aircraft_ceiling} ft)
            - **Reserve fuel recommended:** {(fuel_rate * (0.75 if aircraft == "Airbus A320" else 0.5)):.1f} {fuel_unit} ({reserve_time} reserve)
            - **Total fuel with reserve:** {(total_fuel + fuel_rate * (0.75 if aircraft == "Airbus A320" else 0.5)):.1f} {fuel_unit}
            - **Weather impact:** {'Minimal' if 'clear' in dep_weather.description.lower() and 'clear' in arr_weather.description.lower() else 'Moderate'}
            {f'- **Aircraft type:** Commercial airliner' if aircraft == "Airbus A320" else ''}
        """)
    
    # Pestaña de planificación de vuelo
    with info_tabs[2]:
        # Create altitude profile chart
        st.subheader("Flight Altitude Profile")
        
        # Create data points for the altitude profile
        distance_points = 50
        distances = np.linspace(0, total_distance, distance_points)
        altitudes = []
        for i, d in enumerate(distances):
            progress = i / (distance_points - 1)
            
            # Ajustar las tasas de ascenso y descenso según el tipo de aeronave
            if aircraft == "Airbus A320":
                # Los aviones comerciales tienen un ascenso y descenso más gradual
                climb_factor = 7
                climb_phase = 0.15  # 15% de la distancia para el ascenso
                descent_phase = 0.85  # Comienza el descenso al 85% de la distancia
                variation_factor = 0.02  # Menos variación en crucero
            else:
                # Aeronaves pequeñas
                climb_factor = 10
                climb_phase = 0.1  # 10% de la distancia para el ascenso
                descent_phase = 0.9  # Comienza el descenso al 90% de la distancia
                variation_factor = 0.05  # Más variación en crucero
            
            if progress < climb_phase:  # Climbing phase
                altitude_val = progress * climb_factor * optimal_altitude
            elif progress > descent_phase:  # Descent phase 
                altitude_val = optimal_altitude - (progress - descent_phase) * climb_factor * optimal_altitude
            else:  # Cruise phase
                # Add some small variations to make it look more realistic
                variation = np.sin(progress * 10) * optimal_altitude * variation_factor
                altitude_val = optimal_altitude + variation
            altitudes.append(altitude_val)
        
        # Create DataFrame for the chart
        chart_data = pd.DataFrame({
            'Distance (km)': distances,
            'Altitude (feet)': altitudes
        })
          # Create the chart with dark theme compatible colors
        altitude_chart = alt.Chart(chart_data).mark_line(
            color='#60a5fa', 
            point=alt.OverlayMarkDef(color='#60a5fa', size=50)
        ).encode(
            x=alt.X('Distance (km)', title='Distance (km)'),
            y=alt.Y('Altitude (feet)', title='Altitude (feet)', scale=alt.Scale(zero=True)),
            tooltip=['Distance (km)', 'Altitude (feet)']
        ).properties(
            width='container',
            height=300,
            title='Predicted Altitude Profile'
        ).configure_title(
            fontSize=16,
            anchor='start',
            color='#e2e8f0'
        ).configure_axis(
            labelColor='#e2e8f0',
            titleColor='#e2e8f0',
            gridColor='#374151'
        ).configure_view(
            strokeWidth=0,
            fill='rgba(30, 41, 59, 0.4)'
        )
        
        st.altair_chart(altitude_chart, use_container_width=True)
        
        # Add textual explanation
        st.caption("This chart shows the planned altitude profile for your flight, including climb, cruise, and descent phases.")
        
        # Add visual fuel gauge
        st.subheader("Fuel Planning")
        col1, col2 = st.columns([1, 4])
        with col1:
            st.markdown("**Fuel:**")
        with col2:
            fuel_percent = min(100, (total_fuel / (fuel_rate * 4)) * 100)  # Scale to a 4-hour reference flight
            st.progress(fuel_percent / 100)
            st.caption(f"Fuel consumption: {fuel_rate} {fuel_unit}/h")
    
    # Pestaña para el informe
    with info_tabs[3]:
        # Import our report utilities
        from report_utils import generate_flight_plan_csv, get_table_download_link
        
        # Prepare flight data dictionary for report
        flight_data = {
            'origin': st.session_state['origin'],
            'destination': st.session_state['destination'],
            'distance': total_distance,
            'aircraft': aircraft,
            'speed': selected_speed,
            'time': estimated_time,
            'fuel': total_fuel,
            'dep_weather': str(dep_weather),
            'arr_weather': str(arr_weather),
            'dep_weather_details': {
                'temperature': dep_weather.temperature,
                'conditions': dep_weather.description,
                'wind_speed': dep_weather.wind_speed,
                'humidity': dep_weather.humidity,
                'pressure': dep_weather.pressure
            },
            'arr_weather_details': {
                'temperature': arr_weather.temperature,
                'conditions': arr_weather.description,
                'wind_speed': arr_weather.wind_speed,
                'humidity': arr_weather.humidity,
                'pressure': arr_weather.pressure
            }
        }
        
        # Generate CSV report
        csv_data = generate_flight_plan_csv(flight_data)
        
        # Create download button with custom styling
        date_str = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"flight_plan_{st.session_state['origin']}_{st.session_state['destination']}_{date_str}.csv"
        
        st.subheader("Flight Plan Report")
        st.markdown("Download or print a complete flight plan for your journey.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(get_table_download_link(
                csv_data, 
                filename,
                "💾 Download Flight Plan (CSV)"
            ), unsafe_allow_html=True)
            
        with col2:
            if st.button("🖨️ Print Flight Plan", use_container_width=True):
                # Import HTML generation function
                from report_utils import create_flight_summary_html
                
                # Generate the HTML for the flight summary
                html_content = create_flight_summary_html(flight_data)
                
                # Display the HTML in an iframe
                st.markdown("### Flight Plan Preview (Ready to Print)")
                st.markdown(f"""
                    <iframe srcdoc='{html_content}' width='100%' height='600' style='border: 1px solid #ddd; border-radius: 8px;'></iframe>
                    <script>
                        // Auto-print functionality would go here in a real app
                    </script>
                """, unsafe_allow_html=True)
