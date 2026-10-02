from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    to_timestamp,
    to_date,
    hour,
    dayofweek
)

# Start Spark
spark = SparkSession.builder \
    .appName("WeatherAirQualityCleaning") \
    .config("spark.hadoop.fs.file.impl.disable.cache", "true") \
    .getOrCreate()

# Input file inside the project
input_file = (
    r"C:\Users\Isha\OneDrive\Desktop"
    r"\weather-air-quality-data-pipeline"
    r"\data\processed"
    r"\combined_weather_air_quality.json"
)

# Output location OUTSIDE OneDrive
output_path = r"C:\weather_pipeline_output\cleaned_weather_air_quality"

# Read combined JSON
df = spark.read \
    .option("multiLine", "true") \
    .json(input_file)

# Convert timestamp
df = df.withColumn(
    "timestamp",
    to_timestamp(col("timestamp"), "yyyy-MM-dd'T'HH:mm")
)

# Add date
df = df.withColumn(
    "date",
    to_date(col("timestamp"))
)

# Add hour
df = df.withColumn(
    "hour",
    hour(col("timestamp"))
)

# Add day of week
df = df.withColumn(
    "day_of_week",
    dayofweek(col("timestamp"))
)

# Remove duplicate city + timestamp records
df = df.dropDuplicates(["city", "timestamp"])

# Record count
print("Cleaned record count:", df.count())

# Display schema
print("\nSchema:")
df.printSchema()

# Display sample
print("\nSample cleaned data:")
df.orderBy("timestamp").show(10, truncate=False)

# Convert processed Spark DataFrame to JSON records
processed_data = [
    row.asDict()
    for row in df.collect()
]

# Save processed data as JSON
import json

output_json = r"C:\weather_pipeline_output\processed_weather_air_quality.json"

with open(output_json, "w", encoding="utf-8") as f:
    json.dump(processed_data, f, indent=4, default=str)

print("\nProcessed JSON data saved to:")
print(output_json)

print("Processed record count:", len(processed_data))