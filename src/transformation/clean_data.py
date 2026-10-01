from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_timestamp


# Create Spark session
spark = (
    SparkSession.builder
    .appName("WeatherAirQualityCleaning")
    .master("local[*]")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")


# Input and output paths
input_path = "data/processed/combined_weather_air_quality.json"
output_path = "data/processed/cleaned_weather_air_quality.json"


# Read JSON data
df = spark.read.option("multiLine", "true").json(input_path)

print("\n========== ORIGINAL DATA ==========")
print(f"Records: {df.count()}")


# Remove duplicate records
df_clean = df.dropDuplicates()


# Convert timestamp to proper timestamp type
df_clean = df_clean.withColumn(
    "timestamp_parsed",
    to_timestamp(col("timestamp"))
)


# Remove records with invalid timestamps
df_clean = df_clean.filter(
    col("timestamp_parsed").isNotNull()
)


# Keep only valid weather values
df_clean = df_clean.filter(
    (col("humidity_percent") >= 0) &
    (col("humidity_percent") <= 100) &
    (col("pm2_5").isNull() | (col("pm2_5") >= 0)) &
    (col("pm10").isNull() | (col("pm10") >= 0)) &
    (col("precipitation_mm") >= 0)
)


# Remove temporary parsed timestamp column
df_clean = df_clean.drop("timestamp_parsed")


print("\n========== CLEANED DATA ==========")
print(f"Records: {df_clean.count()}")


# Show missing values
print("\n========== MISSING VALUES AFTER CLEANING ==========")

for column in df_clean.columns:
    missing = df_clean.filter(col(column).isNull()).count()
    print(f"{column}: {missing}")


# Show sample records
print("\n========== SAMPLE CLEANED DATA ==========")
df_clean.show(5, truncate=False)


# Collect cleaned data to Python
cleaned_records = [row.asDict() for row in df_clean.collect()]

# Write using Python instead of Spark/Hadoop
import json
import os

os.makedirs("data/processed", exist_ok=True)

with open(output_path, "w", encoding="utf-8") as file:
    json.dump(cleaned_records, file, indent=4, default=str)

print("\n========== CLEANING COMPLETE ==========")
print(f"Records written: {len(cleaned_records)}")
print(f"Output: {output_path}")

# Stop Spark
spark.stop()