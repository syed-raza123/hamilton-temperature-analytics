
-- Hamilton Temperature Analytics
-- October 14, 2026
-- Dataset: Hamilton hourly temperatures, 2025

-- 1. Create table (already completed)
CREATE TABLE IF NOT EXISTS hamilton_weather (
    recorded_at TIMESTAMP,
    temperature_c NUMERIC
);

-- 2. CSV import
-- Run the following in psql from the project root.
-- Already imported successfully: COPY 8760.
-- Do not rerun the import on a populated table.
-- \copy public.hamilton_weather (recorded_at, temperature_c) FROM 'data/hamilton_weather_2025_clean.csv' WITH (FORMAT csv, HEADER true);

-- 3. Total observations
SELECT COUNT(*) AS total_observations
FROM hamilton_weather;

-- 4. Earliest and latest timestamps
SELECT
    MIN(recorded_at) AS first_reading,
    MAX(recorded_at) AS last_reading
FROM hamilton_weather;

-- 5. Temperature extremes
SELECT
    MIN(temperature_c) AS lowest_temp,
    MAX(temperature_c) AS highest_temp
FROM hamilton_weather;

-- 6. Missing values
SELECT
    COUNT(*) - COUNT(temperature_c) AS missing_temperatures,
    COUNT(*) - COUNT(recorded_at) AS missing_timestamps
FROM hamilton_weather;

-- 7. Duplicate timestamps
SELECT
    COUNT(*) - COUNT(DISTINCT recorded_at) AS duplicate_timestamps
FROM hamilton_weather;

-- 8. Exact duplicate groups
SELECT
    recorded_at,
    temperature_c,
    COUNT(*) AS occurrences
FROM hamilton_weather
GROUP BY recorded_at, temperature_c
HAVING COUNT(*) > 1;
