
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


-- ========================================
-- OCTOBER 16: AGGREGATION AND GROUPING
-- ========================================
-- Daily and hourly temperature analysis
-- Dataset: Hamilton weather, 2025

-- 1. Average daily temperature
SELECT recorded_at::date AS weather_date,
       ROUND(AVG(temperature_c), 1) AS daily_avg_c
FROM hamilton_weather
GROUP BY weather_date
ORDER BY weather_date ASC;

-- 2. Average temperature by hour of day
SELECT EXTRACT(HOUR FROM recorded_at) AS hour_of_day,
       ROUND(AVG(temperature_c), 1) AS hourly_avg_c
FROM hamilton_weather
GROUP BY hour_of_day
ORDER BY hour_of_day DESC;

-- 3. Daily minimum, maximum, and average
SELECT recorded_at::date AS weather_date,
       MIN(temperature_c) AS daily_min_c,
       MAX(temperature_c) AS daily_max_c,
       ROUND(AVG(temperature_c), 1) AS daily_avg_c
FROM hamilton_weather
GROUP BY weather_date
ORDER BY weather_date ASC;


-- ==================================================
-- OCTOBER 17: REAL TEMPERATURE ANALYSIS
-- Hamilton, Ontario | 2025 Hourly Weather Data
-- ==================================================

-- 1. WARMEST RECORDED HOUR
SELECT recorded_at, temperature_c
FROM hamilton_weather
ORDER BY temperature_c DESC
LIMIT 1;

-- 2. COLDEST RECORDED HOUR
SELECT recorded_at, temperature_c
FROM hamilton_weather
ORDER BY temperature_c ASC
LIMIT 1;

-- 3. WARMEST DAY BY AVERAGE TEMPERATURE
SELECT
    recorded_at::date AS day,
    ROUND(AVG(temperature_c)::numeric, 2) AS avg_temp
FROM hamilton_weather
GROUP BY recorded_at::date
ORDER BY avg_temp DESC
LIMIT 1;

-- 4. COLDEST DAY BY AVERAGE TEMPERATURE
SELECT
    recorded_at::date AS day,
    ROUND(AVG(temperature_c)::numeric, 2) AS avg_temp
FROM hamilton_weather
GROUP BY recorded_at::date
ORDER BY avg_temp ASC
LIMIT 1;

-- 5. DAILY TEMPERATURE RANGES
SELECT
    recorded_at::date AS day,
    MAX(temperature_c) AS max_temp,
    MIN(temperature_c) AS min_temp,
    ROUND(
        (MAX(temperature_c) - MIN(temperature_c))::numeric,
        2
    ) AS daily_range
FROM hamilton_weather
GROUP BY recorded_at::date
ORDER BY day ASC;

-- 6. TOP 5 DAYS WITH GREATEST FLUCTUATIONS
SELECT
    recorded_at::date AS day,
    MAX(temperature_c) AS max_temp,
    MIN(temperature_c) AS min_temp,
    ROUND(
        (MAX(temperature_c) - MIN(temperature_c))::numeric,
        2
    ) AS daily_range
FROM hamilton_weather
GROUP BY recorded_at::date
ORDER BY daily_range DESC
LIMIT 5;

-- 7. MORNING VS AFTERNOON TEMPERATURES
SELECT
    CASE
        WHEN EXTRACT(HOUR FROM recorded_at)
            BETWEEN 6 AND 11
        THEN 'Morning'
        ELSE 'Afternoon'
    END AS day_period,
    ROUND(AVG(temperature_c)::numeric, 2) AS avg_temp_c,
    COUNT(*) AS readings
FROM hamilton_weather
WHERE EXTRACT(HOUR FROM recorded_at)
    BETWEEN 6 AND 17
GROUP BY day_period
ORDER BY day_period;

-- 8. MONTHLY EXTREME TEMPERATURE FREQUENCY
SELECT
    EXTRACT(MONTH FROM recorded_at)::int AS month,
    COUNT(*) FILTER (
        WHERE temperature_c > 30
    ) AS hot_hours,
    COUNT(*) FILTER (
        WHERE temperature_c < 0
    ) AS freezing_hours
FROM hamilton_weather
GROUP BY EXTRACT(MONTH FROM recorded_at)
ORDER BY month ASC;

-- 9. FINAL DATA VERIFICATION
SELECT
    COUNT(*) AS total_readings,
    COUNT(DISTINCT recorded_at) AS unique_timestamps,
    COUNT(DISTINCT recorded_at::date) AS total_days,
    MIN(recorded_at) AS first_timestamp,
    MAX(recorded_at) AS last_timestamp,
    MIN(temperature_c) AS min_temp,
    MAX(temperature_c) AS max_temp,
    COUNT(*) FILTER (
        WHERE temperature_c > 30
    ) AS hot_hours,
    COUNT(*) FILTER (
        WHERE temperature_c < 0
    ) AS freezing_hours
FROM hamilton_weather;

-- ============================================================
-- OCTOBER 22: ADVANCED SQL JOIN ANALYSIS
-- Hamilton Temperature Analytics | 2025
-- ============================================================

-- QUERY 1: Combine calendar and daily weather information
-- Expected: 365 matching daily records

SELECT
    c.date,
    c.day_name,
    c.month_name,
    c.is_weekend,
    d.hourly_observations,
    d.avg_temperature_c,
    d.min_temperature_c,
    d.max_temperature_c
FROM public.calendar AS c
INNER JOIN public.daily_temperature_summary AS d
    ON c.date = d.weather_date
ORDER BY c.date;


-- QUERY 2: Identify calendar dates missing weather summaries
-- Expected: 0 rows

SELECT
    c.date,
    c.day_name
FROM public.calendar AS c
LEFT JOIN public.daily_temperature_summary AS d
    ON c.date = d.weather_date
WHERE d.weather_date IS NULL
ORDER BY c.date;


-- QUERY 3: Compare weekdays and weekends
-- Finding: Weekends averaged 9.04 C;
-- weekdays averaged 8.77 C.

SELECT
    CASE
        WHEN c.is_weekend = TRUE THEN 'Weekend'
        ELSE 'Weekday'
    END AS day_type,
    COUNT(*) AS total_days,
    ROUND(AVG(d.avg_temperature_c), 2)
        AS avg_temperature_c,
    MIN(d.min_temperature_c)
        AS lowest_temperature_c,
    MAX(d.max_temperature_c)
        AS highest_temperature_c
FROM public.calendar AS c
INNER JOIN public.daily_temperature_summary AS d
    ON c.date = d.weather_date
GROUP BY c.is_weekend
ORDER BY c.is_weekend;


-- QUERY 4: Monthly temperature analysis
-- Finding: July was warmest at 23.97 C;
-- February was coldest at -5.52 C.

SELECT
    c.month_number,
    c.month_name,
    COUNT(*) AS total_days,
    ROUND(AVG(d.avg_temperature_c), 2)
        AS avg_temperature_c,
    MIN(d.min_temperature_c)
        AS lowest_temperature_c,
    MAX(d.max_temperature_c)
        AS highest_temperature_c
FROM public.calendar AS c
INNER JOIN public.daily_temperature_summary AS d
    ON c.date = d.weather_date
GROUP BY c.month_number, c.month_name
ORDER BY c.month_number;


-- QUERY 5: Find the 10 hottest days of 2025
-- Ranked by maximum hourly temperature
-- Finding: June 23 reached 36.2 C.

SELECT
    c.date,
    c.day_name,
    c.month_name,
    d.avg_temperature_c,
    d.min_temperature_c,
    d.max_temperature_c
FROM public.calendar AS c
INNER JOIN public.daily_temperature_summary AS d
    ON c.date = d.weather_date
ORDER BY d.max_temperature_c DESC,
         c.date ASC
LIMIT 10;


-- QUERY 6: Validate joined record counts
-- Expected: 365 days and 8760 hourly observations

SELECT
    COUNT(*) AS matched_days,
    SUM(d.hourly_observations) AS total_hourly_records,
    MIN(c.date) AS first_date,
    MAX(c.date) AS last_date
FROM public.calendar AS c
INNER JOIN public.daily_temperature_summary AS d
    ON c.date = d.weather_date;


-- QUERY 7: Check for duplicate dates after the JOIN
-- Expected: 0 rows

SELECT
    c.date,
    COUNT(*) AS times_appearing
FROM public.calendar AS c
INNER JOIN public.daily_temperature_summary AS d
    ON c.date = d.weather_date
GROUP BY c.date
HAVING COUNT(*) > 1
ORDER BY c.date;

-- ============================================================
-- END OF OCTOBER 22 JOIN ANALYSIS
-- ============================================================