from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_timestamp

# Create Spark session
spark = SparkSession.builder \
    .appName("WeatherAirQualityValidation") \
    .getOrCreate()

# Read combined JSON
df = spark.read \
    .option("multiline", "true") \
    .json("data/processed/combined_weather_air_quality.json")

print("\n========== INITIAL RECORD COUNT ==========")
print("Records:", df.count())

# --------------------------------------------------
# 1. Check missing values
# --------------------------------------------------

print("\n========== MISSING VALUES ==========")

for column in df.columns:
    missing = df.filter(col(column).isNull()).count()
    print(f"{column}: {missing}")


# 2. Check duplicate records

print("\n========== DUPLICATES ==========")

duplicate_count = df.count() - df.dropDuplicates().count()

print("Duplicate records:", duplicate_count)

# 3. Validate humidity
print("\n========== HUMIDITY VALIDATION ==========")

invalid_humidity = df.filter(
    (col("humidity_percent") < 0) |
    (col("humidity_percent") > 100)
).count()

print("Invalid humidity records:", invalid_humidity)

# 4. Validate PM2.5

print("\n========== PM2.5 VALIDATION ==========")

invalid_pm25 = df.filter(
    col("pm2_5") < 0
).count()

print("Invalid PM2.5 records:", invalid_pm25)

# --------------------------------------------------
# 5. Validate PM10
# --------------------------------------------------

print("\n========== PM10 VALIDATION ==========")

invalid_pm10 = df.filter(
    col("pm10") < 0
).count()

print("Invalid PM10 records:", invalid_pm10)

# 6. Validate precipitation

print("\n========== PRECIPITATION VALIDATION ==========")

invalid_precipitation = df.filter(
    col("precipitation_mm") < 0
).count()

print("Invalid precipitation records:", invalid_precipitation)

# 7. Validate city

print("\n========== CITY VALIDATION ==========")

invalid_city = df.filter(
    col("city").isNull() | (col("city") == "")
).count()

print("Invalid city records:", invalid_city)


# 8. Validate timestamp


print("\n========== TIMESTAMP VALIDATION ==========")

df = df.withColumn(
    "timestamp_parsed",
    to_timestamp(col("timestamp"), "yyyy-MM-dd'T'HH:mm")
)

invalid_timestamp = df.filter(
    col("timestamp_parsed").isNull()
).count()

print("Invalid timestamp records:", invalid_timestamp)


# 9. Show invalid records


print("\n========== INVALID RECORDS ==========")

df.filter(
    (col("humidity_percent") < 0) |
    (col("humidity_percent") > 100) |
    (col("pm2_5") < 0) |
    (col("pm10") < 0) |
    (col("precipitation_mm") < 0) |
    col("city").isNull() |
    (col("city") == "") |
    col("timestamp_parsed").isNull()
).show(truncate=False)

spark.stop()