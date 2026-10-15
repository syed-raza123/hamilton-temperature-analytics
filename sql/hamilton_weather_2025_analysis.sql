
-- Hamilton Temperature Analytics
-- Historical weather analysis for Hamilton, Ontario
-- Dataset: Open-Meteo, January 1 - December 31, 2025
-- Table: hamilton_weather
-- Authoring date: October 15, 2026


-- ==========================================
-- SECTION 1: SQL QUERYING FUNDAMENTALS
-- ==========================================

-- 1. Preview the weather observations

SELECT recorded_at, temperature_c
FROM hamilton_weather
LIMIT 10;


-- 2. Filter temperatures using WHERE and AND

SELECT recorded_at, temperature_c
FROM hamilton_weather
WHERE temperature_c >= 15
AND temperature_c < 25;


-- 3. Filter extreme temperatures using OR

SELECT recorded_at, temperature_c
FROM hamilton_weather
WHERE temperature_c < -5
OR temperature_c >= 30;


-- 4. Filter a temperature range using BETWEEN

SELECT recorded_at, temperature_c
FROM hamilton_weather
WHERE temperature_c BETWEEN 18 AND 27;


-- ==========================================
-- SECTION 2: AGGREGATE FUNCTIONS
-- ==========================================

-- 5. Count the total hourly observations

SELECT COUNT(*) AS total_hours
FROM hamilton_weather;


-- 6. Calculate the average annual temperature

SELECT AVG(temperature_c) AS average_temperature
FROM hamilton_weather;


-- 7. Find the minimum recorded temperature

SELECT MIN(temperature_c) AS minimum_temperature
FROM hamilton_weather;


-- 8. Find the maximum recorded temperature

SELECT MAX(temperature_c) AS maximum_temperature
FROM hamilton_weather;


-- ==========================================
-- SECTION 3: WEATHER ANALYSIS
-- ==========================================

-- 9. Find the five hottest recorded hours
-- Highest: 36.2 C on June 23, 2025, at 16:00

SELECT recorded_at, temperature_c
FROM hamilton_weather
ORDER BY temperature_c DESC
LIMIT 5;


-- 10. Find the five coldest recorded hours
-- Lowest: -19.9 C on January 22, 2025, at 09:00

SELECT recorded_at, temperature_c
FROM hamilton_weather
ORDER BY temperature_c ASC
LIMIT 5;


-- 11. Count hours strictly above 30 C
-- Verified result: 165 hours

SELECT COUNT(*) AS hours_above_30
FROM hamilton_weather
WHERE temperature_c > 30;


-- 12. Count hours strictly below 0 C
-- Verified result: 2285 hours

SELECT COUNT(*) AS hours_below_zero
FROM hamilton_weather
WHERE temperature_c < 0;
