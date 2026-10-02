SELECT COUNT(*) AS record_count
FROM `weather-aq-pipeline.weather_staging.weather_air_quality_staging`;


SELECT
  COUNT(*) AS total_records,
  COUNTIF(timestamp IS NULL) AS null_timestamps,
  COUNTIF(city IS NULL) AS null_cities,
  COUNTIF(humidity_percent < 0 OR humidity_percent > 100) AS invalid_humidity,
  COUNTIF(pm2_5 < 0) AS invalid_pm25,
  COUNTIF(pm10 < 0) AS invalid_pm10,
  COUNTIF(precipitation_mm < 0) AS invalid_precipitation
FROM `weather-aq-pipeline.weather_staging.weather_air_quality_staging`;


CREATE OR REPLACE TABLE
`weather-aq-pipeline.weather_warehouse.weather_air_quality_analytics` AS

SELECT
    city,
    timestamp,

    DATE(timestamp) AS weather_date,
    EXTRACT(YEAR FROM timestamp) AS year,
    EXTRACT(MONTH FROM timestamp) AS month,
    EXTRACT(DAY FROM timestamp) AS day,
    EXTRACT(HOUR FROM timestamp) AS hour,

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
`weather-aq-pipeline.weather_staging.weather_air_quality_staging`

WHERE timestamp IS NOT NULL
  AND city IS NOT NULL;

SELECT COUNT(*) AS record_count
FROM `weather-aq-pipeline.weather_warehouse.weather_air_quality_analytics`;


SELECT
    weather_date,
    ROUND(AVG(temperature_c), 2) AS avg_temperature_c,
    ROUND(AVG(humidity_percent), 2) AS avg_humidity_percent,
    ROUND(AVG(pm2_5), 2) AS avg_pm2_5,
    ROUND(AVG(pm10), 2) AS avg_pm10,
    ROUND(AVG(european_aqi), 2) AS avg_aqi
FROM
    `weather-aq-pipeline.weather_warehouse.weather_air_quality_analytics`
GROUP BY
    weather_date
ORDER BY
    weather_date;


SELECT
    hour,
    ROUND(AVG(temperature_c), 2) AS avg_temperature_c,
    ROUND(AVG(humidity_percent), 2) AS avg_humidity_percent,
    ROUND(AVG(pm2_5), 2) AS avg_pm2_5,
    ROUND(AVG(pm10), 2) AS avg_pm10,
    ROUND(AVG(european_aqi), 2) AS avg_aqi
FROM
    `weather-aq-pipeline.weather_warehouse.weather_air_quality_analytics`
GROUP BY
    hour
ORDER BY
    hour;


SELECT
    timestamp,
    city,
    temperature_c,
    humidity_percent,
    pm2_5,
    pm10,
    european_aqi
FROM
    `weather-aq-pipeline.weather_warehouse.weather_air_quality_analytics`
ORDER BY
    european_aqi DESC
LIMIT 10;