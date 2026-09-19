import json
from pathlib import Path

import requests

# Configuration

LATITUDE = 18.5204
LONGITUDE = 73.8567
TIMEZONE = "Asia/Kolkata"

WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

# API Functions

def fetch_weather():
    """Fetch weather data from Open-Meteo."""

    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "hourly": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "pressure_msl,"
            "wind_speed_10m,"
            "precipitation"
        ),
        "timezone": TIMEZONE,
        "forecast_hours": 168,
    }

    response = requests.get(WEATHER_URL, params=params, timeout=30)
    response.raise_for_status()

    return response.json()


def fetch_air_quality():
    """Fetch air-quality data from Open-Meteo."""

    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "hourly": (
            "pm2_5,"
            "pm10,"
            "nitrogen_dioxide,"
            "ozone,"
            "carbon_monoxide,"
            "european_aqi"
        ),
        "timezone": TIMEZONE,
        "forecast_hours": 168,
    }

    response = requests.get(AIR_QUALITY_URL, params=params, timeout=30)
    response.raise_for_status()

    return response.json()

# Main Program
def main():
    print("Fetching weather data...")
    weather_data = fetch_weather()

    print("Fetching air-quality data...")
    air_quality_data = fetch_air_quality()

    # Create raw data directory
    raw_dir = Path("data/raw")
    raw_dir.mkdir(parents=True, exist_ok=True)

    # Save weather response
    weather_file = raw_dir / "weather_raw.json"
    with open(weather_file, "w", encoding="utf-8") as file:
        json.dump(weather_data, file, indent=4)

    # Save air-quality response
    air_quality_file = raw_dir / "air_quality_raw.json"
    with open(air_quality_file, "w", encoding="utf-8") as file:
        json.dump(air_quality_data, file, indent=4)

    print("\nData fetched successfully.")
    print(f"Weather data saved to: {weather_file}")
    print(f"Air-quality data saved to: {air_quality_file}")


if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()