CREATE OR REPLACE TABLE
`weather-aq-pipeline.weather_warehouse.dim_date` AS
SELECT DISTINCT
    date AS date_key,
    EXTRACT(YEAR FROM date) AS year,
    EXTRACT(MONTH FROM date) AS month,
    EXTRACT(DAY FROM date) AS day,
    EXTRACT(DAYOFWEEK FROM date) AS day_of_week
FROM
`weather-aq-pipeline.weather_staging.weather_air_quality_pyspark`
WHERE date IS NOT NULL
ORDER BY date;


SELECT *
FROM `weather-aq-pipeline.weather_warehouse.dim_date`
ORDER BY date_key;

CREATE OR REPLACE TABLE
`weather-aq-pipeline.weather_warehouse.dim_location` AS
SELECT DISTINCT
    city AS location_key,
    city
FROM
`weather-aq-pipeline.weather_staging.weather_air_quality_pyspark`
WHERE city IS NOT NULL;

SELECT *
FROM `weather-aq-pipeline.weather_warehouse.dim_location`;


CREATE OR REPLACE TABLE
`weather-aq-pipeline.weather_warehouse.fact_weather_air_quality` AS
SELECT
    timestamp,
    city AS location_key,
    date AS date_key,
    temperature_c,
    humidity_percent,
    pressure_hpa,
    wind_speed_kmh,
    precipitation_mm,
    pm2_5,
    pm10,
    nitrogen_dioxide,
    ozone,
    carbon_monoxide,
    european_aqi
FROM
`weather-aq-pipeline.weather_staging.weather_air_quality_pyspark`
WHERE timestamp IS NOT NULL
  AND city IS NOT NULL
  AND date IS NOT NULL;

SELECT COUNT(*) AS record_count
FROM `weather-aq-pipeline.weather_warehouse.fact_weather_air_quality`;

