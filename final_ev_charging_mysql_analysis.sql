-- ============================================================
-- FINAL INDIA EV CHARGING INFRASTRUCTURE ANALYSIS
-- Source: ev_charging_stations_india_final_consistent.csv
-- Master rows: 1222
-- MySQL 8.0+
-- ============================================================

-- 1) Create database / table
CREATE DATABASE IF NOT EXISTS ev_charging;
USE ev_charging;

DROP TABLE IF EXISTS ev_charging_stations;

CREATE TABLE ev_charging_stations (
    name VARCHAR(255) NOT NULL,
    state VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    address VARCHAR(500) NOT NULL,
    latitude DECIMAL(10,6) NOT NULL,
    longitude DECIMAL(10,6) NOT NULL,
    INDEX idx_state (state),
    INDEX idx_city (city),
    INDEX idx_state_city (state, city),
    INDEX idx_name (name)
);

-- Load the final clean CSV.
-- Update the file path for your local machine.
-- Example for Windows:
-- LOAD DATA LOCAL INFILE 'C:/Users/YourName/Downloads/ev_charging_stations_india_final_consistent.csv'
-- INTO TABLE ev_charging_stations
-- FIELDS TERMINATED BY ',' ENCLOSED BY '"'
-- LINES TERMINATED BY '\n'
-- IGNORE 1 ROWS
-- (name, state, city, address, latitude, longitude);

-- ============================================================
-- DATA QUALITY CHECKS
-- ============================================================

-- Q1. Total station records
SELECT COUNT(*) AS total_station_records
FROM ev_charging_stations;

-- Q2. Number of states and cities
SELECT
    COUNT(DISTINCT state) AS states_covered,
    COUNT(DISTINCT city) AS cities_covered
FROM ev_charging_stations;

-- Q3. Missing values in critical fields
SELECT
    SUM(name IS NULL OR TRIM(name) = '') AS missing_name,
    SUM(state IS NULL OR TRIM(state) = '') AS missing_state,
    SUM(city IS NULL OR TRIM(city) = '') AS missing_city,
    SUM(address IS NULL OR TRIM(address) = '') AS missing_address,
    SUM(latitude IS NULL) AS missing_latitude,
    SUM(longitude IS NULL) AS missing_longitude
FROM ev_charging_stations;

-- Q4. Duplicate rows using all six fields
SELECT
    COUNT(*) - COUNT(DISTINCT CONCAT_WS('|', name, state, city, address,
                                        latitude, longitude)) AS duplicate_like_rows
FROM ev_charging_stations;

-- Q5. City mapped to more than one state (should return zero rows)
SELECT city, COUNT(DISTINCT state) AS state_count
FROM ev_charging_stations
GROUP BY city
HAVING COUNT(DISTINCT state) > 1
ORDER BY state_count DESC, city;

-- Q6. Coordinate range check
SELECT COUNT(*) AS invalid_coordinate_rows
FROM ev_charging_stations
WHERE latitude NOT BETWEEN 5 AND 38
   OR longitude NOT BETWEEN 67 AND 99;

-- ============================================================
-- GEOGRAPHIC ANALYSIS
-- ============================================================

-- Q7. Top states by station records
SELECT
    state,
    COUNT(*) AS stations,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM ev_charging_stations), 2) AS share_pct
FROM ev_charging_stations
GROUP BY state
ORDER BY stations DESC, state;

-- Q8. Top 5-state concentration
WITH state_counts AS (
    SELECT state, COUNT(*) AS stations
    FROM ev_charging_stations
    GROUP BY state
)
SELECT
    SUM(stations) AS top_5_stations,
    ROUND(SUM(stations) * 100.0 / (SELECT COUNT(*) FROM ev_charging_stations), 2) AS top_5_share_pct
FROM (
    SELECT stations
    FROM state_counts
    ORDER BY stations DESC
    LIMIT 5
) x;

-- Q9. Top city-state combinations
SELECT
    city,
    state,
    COUNT(*) AS stations
FROM ev_charging_stations
GROUP BY city, state
ORDER BY stations DESC, state, city
LIMIT 15;

-- Q10. States with the broadest city coverage
SELECT
    state,
    COUNT(DISTINCT city) AS cities_covered,
    COUNT(*) AS stations
FROM ev_charging_stations
GROUP BY state
ORDER BY cities_covered DESC, stations DESC
LIMIT 15;

-- Q11. Cities with more than 10 station records
SELECT
    city,
    state,
    COUNT(*) AS stations
FROM ev_charging_stations
GROUP BY city, state
HAVING COUNT(*) > 10
ORDER BY stations DESC, state, city;

-- Q12. Average station records per city by state
SELECT
    state,
    COUNT(*) AS stations,
    COUNT(DISTINCT city) AS cities,
    ROUND(COUNT(*) * 1.0 / COUNT(DISTINCT city), 2) AS avg_stations_per_city
FROM ev_charging_stations
GROUP BY state
ORDER BY avg_stations_per_city DESC, stations DESC;

-- ============================================================
-- STATION NAME / SITE CLUSTER ANALYSIS
-- ============================================================

-- Q13. Repeated station-name values
SELECT
    name,
    COUNT(*) AS records,
    COUNT(DISTINCT state) AS states,
    COUNT(DISTINCT city) AS cities
FROM ev_charging_stations
GROUP BY name
HAVING COUNT(*) > 1
ORDER BY records DESC, name;

-- Q14. Name repetition summary
SELECT
    SUM(name_frequency = 1) AS names_used_once,
    SUM(name_frequency > 1) AS repeated_name_values
FROM (
    SELECT name, COUNT(*) AS name_frequency
    FROM ev_charging_stations
    GROUP BY name
) t;

-- Q15. Exact coordinate/site clusters
SELECT
    latitude,
    longitude,
    COUNT(*) AS records
FROM ev_charging_stations
GROUP BY latitude, longitude
HAVING COUNT(*) > 1
ORDER BY records DESC;

-- Q16. Share of records using unique coordinate pairs
SELECT
    COUNT(DISTINCT CONCAT(latitude, '|', longitude)) AS unique_coordinate_pairs,
    COUNT(*) AS total_records,
    ROUND(
        COUNT(DISTINCT CONCAT(latitude, '|', longitude)) * 100.0 / COUNT(*),
        2
    ) AS unique_coordinate_share_pct
FROM ev_charging_stations;

-- ============================================================
-- PORTFOLIO / INTERVIEW-READY QUESTIONS
-- ============================================================

-- Q17. What is the share of the largest state?
SELECT
    state,
    COUNT(*) AS stations,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM ev_charging_stations), 2) AS share_pct
FROM ev_charging_stations
GROUP BY state
ORDER BY stations DESC
LIMIT 1;

-- Q18. What is the most represented city?
SELECT
    city,
    state,
    COUNT(*) AS stations
FROM ev_charging_stations
GROUP BY city, state
ORDER BY stations DESC
LIMIT 1;

-- Q19. States with >= 50 station records
SELECT
    state,
    COUNT(*) AS stations
FROM ev_charging_stations
GROUP BY state
HAVING COUNT(*) >= 50
ORDER BY stations DESC;

-- Q20. City concentration within states (top city per state)
WITH city_ranked AS (
    SELECT
        state,
        city,
        COUNT(*) AS stations,
        ROW_NUMBER() OVER (
            PARTITION BY state
            ORDER BY COUNT(*) DESC, city
        ) AS rn
    FROM ev_charging_stations
    GROUP BY state, city
)
SELECT state, city, stations
FROM city_ranked
WHERE rn = 1
ORDER BY stations DESC, state;

-- End of analysis.
