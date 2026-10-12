
-- Hamilton Temperature Analytics
-- October 12: SQL Fundamentals
-- All temperature readings are fictional practice data.

-- Table creation (already executed in pgAdmin).
-- Kept as a comment to avoid recreating the table.

/*
CREATE TABLE temperature_practice (
    reading_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    recorded_at TIMESTAMP NOT NULL,
    temperature_c NUMERIC(5,2) NOT NULL,
    source TEXT NOT NULL
);
*/

-- Query 1: Temperatures 20 degrees or higher.
-- Sorted from coldest to hottest.

SELECT recorded_at, temperature_c
FROM temperature_practice
WHERE temperature_c >= 20
ORDER BY temperature_c ASC;

-- Query 2: Temperatures above 23 degrees.
-- Sorted from hottest to coldest.

SELECT reading_id, temperature_c
FROM temperature_practice
WHERE temperature_c > 23
ORDER BY temperature_c DESC;

-- Query 3: Temperatures 18 degrees or lower.
-- Sorted from coldest to hottest.

SELECT recorded_at, temperature_c, source
FROM temperature_practice
WHERE temperature_c <= 18
ORDER BY temperature_c ASC;
