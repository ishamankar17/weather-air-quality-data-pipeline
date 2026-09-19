import json
from pathlib import Path


RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")


def load_json(file_path):
    """Load a JSON file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def combine_data(weather_data, air_quality_data):
    """Combine weather and air-quality data using timestamp."""

    weather = weather_data["hourly"]
    air_quality = air_quality_data["hourly"]

    air_quality_by_time = {
        time: index
        for index, time in enumerate(air_quality["time"])
    }

    combined_records = []

    for index, timestamp in enumerate(weather["time"]):

        if timestamp not in air_quality_by_time:
            continue

        air_index = air_quality_by_time[timestamp]

        record = {
            "city": "Pune",
            "timestamp": timestamp,

            "temperature_c": weather["temperature_2m"][index],
            "humidity_percent": weather["relative_humidity_2m"][index],
            "pressure_hpa": weather["pressure_msl"][index],
            "wind_speed_kmh": weather["wind_speed_10m"][index],
            "precipitation_mm": weather["precipitation"][index],

            "pm2_5": air_quality["pm2_5"][air_index],
            "pm10": air_quality["pm10"][air_index],
            "nitrogen_dioxide": air_quality["nitrogen_dioxide"][air_index],
            "ozone": air_quality["ozone"][air_index],
            "carbon_monoxide": air_quality["carbon_monoxide"][air_index],
            "european_aqi": air_quality["european_aqi"][air_index]
        }

        combined_records.append(record)

    return combined_records


def main():
    weather_file = RAW_DIR / "weather_raw.json"
    air_quality_file = RAW_DIR / "air_quality_raw.json"

    weather_data = load_json(weather_file)
    air_quality_data = load_json(air_quality_file)

    combined_data = combine_data(weather_data, air_quality_data)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    output_file = PROCESSED_DIR / "combined_weather_air_quality.json"

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(combined_data, file, indent=4)

    print(f"Combined records created: {len(combined_data)}")
    print(f"Saved to: {output_file}")


if __name__ == "__main__":
    main()