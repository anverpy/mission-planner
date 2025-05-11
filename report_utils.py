"""
Helper module for generating flight plan reports
"""
import pandas as pd
from io import BytesIO
import base64
import datetime

def generate_flight_plan_csv(flight_data: dict) -> str:
    """
    Generate a CSV report of the flight plan
    
    Args:
        flight_data: Dictionary containing flight plan details
        
    Returns:
        str: Base64 encoded CSV data for download
    """
    # Create a BytesIO buffer
    buffer = BytesIO()
    
    # Create DataFrame from flight data
    df = pd.DataFrame([{
        'Origin': flight_data.get('origin', 'Unknown'),
        'Destination': flight_data.get('destination', 'Unknown'),
        'Distance (km)': flight_data.get('distance', 0),
        'Aircraft': flight_data.get('aircraft', 'Unknown'),
        'Cruise Speed (km/h)': flight_data.get('speed', 0),
        'Flight Time (hours)': flight_data.get('time', 0),
        'Fuel Required (L)': flight_data.get('fuel', 0),
        'Origin Weather': flight_data.get('dep_weather', 'Unknown'),
        'Destination Weather': flight_data.get('arr_weather', 'Unknown'),
        'Generation Date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }])
    
    # Add weather details as separate columns if available
    if 'dep_weather_details' in flight_data:
        for key, value in flight_data['dep_weather_details'].items():
            df[f'Origin {key.capitalize()}'] = value
    
    if 'arr_weather_details' in flight_data:
        for key, value in flight_data['arr_weather_details'].items():
            df[f'Destination {key.capitalize()}'] = value
    
    # Save to CSV
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    
    # Generate download link
    b64 = base64.b64encode(buffer.read()).decode()
    return b64

def get_table_download_link(b64_data: str, filename: str, link_text: str) -> str:
    """
    Generate HTML for a download link for the given base64 encoded data
    
    Args:
        b64_data: Base64 encoded data
        filename: Name of file to download
        link_text: Text to display for the link
        
    Returns:
        str: HTML for download link
    """
    href = f'<a href="data:file/csv;base64,{b64_data}" download="{filename}" class="download-btn">{link_text}</a>'
    return href

def create_flight_summary_html(flight_data: dict) -> str:
    """
    Create an HTML summary of the flight plan
    
    Args:
        flight_data: Dictionary containing flight plan details
        
    Returns:
        str: HTML representation of flight summary
    """
    # Determine the fuel unit based on aircraft type
    fuel_unit = "kg" if flight_data.get('aircraft') == "Airbus A320" else "L"
    
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; border: 1px solid #4b5563; border-radius: 10px; background-color: #1e293b; color: #e2e8f0;">
        <h2 style="color: #60a5fa; text-align: center; border-bottom: 2px solid #374151; padding-bottom: 10px;">
            Flight Plan Summary
        </h2>
        
        <div style="display: flex; justify-content: space-between; margin-top: 20px;">
            <div style="flex: 1;">
                <p style="font-weight: bold; margin-bottom: 5px; color: #93c5fd;">Origin</p>
                <p style="font-size: 18px;">{flight_data.get('origin', 'Unknown')}</p>
            </div>
            <div style="flex: 0;">
                <p style="font-size: 24px; margin-top: 15px; color: #60a5fa;">→</p>
            </div>
            <div style="flex: 1; text-align: right;">
                <p style="font-weight: bold; margin-bottom: 5px; color: #93c5fd;">Destination</p>
                <p style="font-size: 18px;">{flight_data.get('destination', 'Unknown')}</p>
            </div>
        </div>
        
        <div style="background-color: rgba(30, 41, 59, 0.8); border-radius: 8px; padding: 15px; margin-top: 20px;">
            <h3 style="margin-top: 0; color: #60a5fa;">Flight Details</h3>
            <table style="width: 100%; border-collapse: collapse; color: #e2e8f0;">
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #4b5563;"><strong>Aircraft</strong></td>
                    <td style="padding: 8px; border-bottom: 1px solid #4b5563;">{flight_data.get('aircraft', 'Unknown')}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #4b5563;"><strong>Distance</strong></td>
                    <td style="padding: 8px; border-bottom: 1px solid #4b5563;">{flight_data.get('distance', 0):.1f} km</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #4b5563;"><strong>Cruise Speed</strong></td>
                    <td style="padding: 8px; border-bottom: 1px solid #4b5563;">{flight_data.get('speed', 0)} km/h</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #4b5563;"><strong>Estimated Time</strong></td>
                    <td style="padding: 8px; border-bottom: 1px solid #4b5563;">{flight_data.get('time', 0):.2f} hours</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #4b5563;"><strong>Fuel Required</strong></td>
                    <td style="padding: 8px; border-bottom: 1px solid #4b5563;">{flight_data.get('fuel', 0):.1f} {fuel_unit}</td>
                </tr>
            </table>
        </div>
        
        <div style="display: flex; justify-content: space-between; margin-top: 20px;">
            <div style="flex: 1; background-color: rgba(20, 83, 45, 0.3); padding: 15px; border-radius: 8px; margin-right: 10px; border-left: 4px solid #22c55e;">
                <h3 style="margin-top: 0; color: #4ade80;">Origin Weather</h3>
                <p style="color: #d1fae5;">{flight_data.get('dep_weather', 'No weather data available').replace('\\n', '<br>')}</p>
            </div>
            <div style="flex: 1; background-color: rgba(7, 89, 133, 0.3); padding: 15px; border-radius: 8px; margin-left: 10px; border-left: 4px solid #0ea5e9;">
                <h3 style="margin-top: 0; color: #38bdf8;">Destination Weather</h3>
                <p style="color: #bae6fd;">{flight_data.get('arr_weather', 'No weather data available').replace('\\n', '<br>')}</p>
            </div>
        </div>
        
        <p style="text-align: center; margin-top: 20px; color: #94a3b8; font-size: 12px;">
            Generated on {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        </p>
    </div>
    """
    return html
