import streamlit as st
from openai import OpenAI
import requests
from datetime import datetime, timedelta

# Set up the page
st.set_page_config(page_title="Travel Weather Forecast", layout="wide")

# Sidebar for configuration
with st.sidebar:
    st.title("Travel Weather Forecast")
    api_key = st.text_input("OpenRouter API Key", type="password")

    # Model selection
    weather_models = [
        "openai/gpt-4-turbo-preview",
        "anthropic/claude-3-opus",
        "google/gemini-pro"
    ]
    selected_model = st.selectbox("Select AI Model", weather_models)

    st.markdown("### Settings")
    forecast_days = st.slider("Number of forecast days", 1, 7, 3)
    detailed = st.checkbox("Detailed forecast", value=True)

# Main content area
st.title("🌦️ Travel Weather Forecast")

# Address input
col1, col2 = st.columns(2)
with col1:
    origin = st.text_input("Origin Address", placeholder="e.g., New York, NY")
with col2:
    destination = st.text_input(
        "Destination Address", placeholder="e.g., Los Angeles, CA")

# Function to get coordinates from address


def get_coordinates(address):
    if not address:
        return None
    try:
        response = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": address, "format": "json", "limit": 1},
            headers={
                "User-Agent": "TravelWeatherForecastApp/1.0 (tarikuli@gmail.com)"}
        )
        response.raise_for_status()  # Raises HTTPError for bad responses
        data = response.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
        return None
    except Exception as e:
        st.error(f"Error geocoding address: {e}")
        return None

# Function to get weather data from Open-Meteo API


def get_weather_forecast(lat, lon, days):
    if not lat or not lon:
        return None
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum", "weather_code"],
            "timezone": "auto",
            "forecast_days": days
        }
        response = requests.get(url, params=params)
        return response.json()
    except Exception as e:
        st.error(f"Error getting weather data: {e}")
        return None

# Function to interpret weather codes


def interpret_weather_code(code):
    weather_codes = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        56: "Light freezing drizzle",
        57: "Dense freezing drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        66: "Light freezing rain",
        67: "Heavy freezing rain",
        71: "Slight snow fall",
        73: "Moderate snow fall",
        75: "Heavy snow fall",
        77: "Snow grains",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        85: "Slight snow showers",
        86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail"
    }
    return weather_codes.get(code, "Unknown weather condition")

# Function to generate AI analysis


def generate_weather_analysis(origin_data, destination_data, days, model, api_key):
    if not api_key:
        return "Please enter your OpenRouter API key"

    if not origin_data or not destination_data:
        return "Please provide both origin and destination addresses"

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    prompt = f"""
    Analyze these weather forecasts for a trip:
    
    Origin Weather Forecast ({days} days):
    {origin_data}
    
    Destination Weather Forecast ({days} days):
    {destination_data}
    
    Provide a concise comparison and travel recommendations based on the weather differences.
    Highlight any significant weather events or packing suggestions.
    """

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating analysis: {str(e)}"


# Helper function to display weather data in a table


def display_weather_table(weather_data, days):
    if not weather_data:
        return

    daily = weather_data.get("daily", {})
    dates = daily.get("time", [])
    max_temps = daily.get("temperature_2m_max", [])
    min_temps = daily.get("temperature_2m_min", [])
    precip = daily.get("precipitation_sum", [])
    codes = daily.get("weather_code", [])

    table_data = []
    for i in range(min(days, len(dates))):
        table_data.append({
            "Date": dates[i],
            "Max Temp (°C)": max_temps[i],
            "Min Temp (°C)": min_temps[i],
            "Precip (mm)": precip[i],
            "Conditions": interpret_weather_code(codes[i])
        })

    st.table(table_data)

# Helper function to format weather data for AI


def format_weather_data(weather_data, days):
    if not weather_data:
        return "No weather data available"

    daily = weather_data.get("daily", {})
    dates = daily.get("time", [])
    max_temps = daily.get("temperature_2m_max", [])
    min_temps = daily.get("temperature_2m_min", [])
    precip = daily.get("precipitation_sum", [])
    codes = daily.get("weather_code", [])

    result = []
    for i in range(min(days, len(dates))):
        result.append(
            f"{dates[i]}: "
            f"High {max_temps[i]}°C, Low {min_temps[i]}°C, "
            f"{precip[i]}mm precipitation, "
            f"{interpret_weather_code(codes[i])}"
        )

    return "\n".join(result)


# Display weather information
if st.button("Get Weather Forecast"):
    if not origin or not destination:
        st.warning("Please enter both origin and destination addresses")
    else:
        with st.spinner("Getting weather data..."):
            # Get coordinates
            origin_coords = get_coordinates(origin)
            destination_coords = get_coordinates(destination)

            if origin_coords and destination_coords:
                # Get weather data
                origin_weather = get_weather_forecast(
                    origin_coords[0], origin_coords[1], forecast_days)
                destination_weather = get_weather_forecast(
                    destination_coords[0], destination_coords[1], forecast_days)

                if origin_weather and destination_weather:
                    # Display raw data if detailed mode
                    if detailed:
                        col1, col2 = st.columns(2)

                        with col1:
                            st.subheader(f"Origin: {origin}")
                            st.write(
                                f"Coordinates: {origin_coords[0]:.4f}, {origin_coords[1]:.4f}")
                            display_weather_table(
                                origin_weather, forecast_days)

                        with col2:
                            st.subheader(f"Destination: {destination}")
                            st.write(
                                f"Coordinates: {destination_coords[0]:.4f}, {destination_coords[1]:.4f}")
                            display_weather_table(
                                destination_weather, forecast_days)

                    # Generate AI analysis
                    with st.spinner("Generating AI analysis..."):
                        origin_data = format_weather_data(
                            origin_weather, forecast_days)
                        destination_data = format_weather_data(
                            destination_weather, forecast_days)
                        analysis = generate_weather_analysis(
                            origin_data, destination_data, forecast_days, selected_model, api_key)

                        st.subheader("🌍 Travel Weather Analysis")
                        st.write(analysis)
                else:
                    st.error("Could not retrieve weather data for both locations")
