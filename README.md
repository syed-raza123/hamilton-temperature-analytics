# hamilton-temperature-analytics
SQL-based temperature analytics project
# Hamilton Temperature Analytics

## Project Overview
This project explores temperature patterns in Hamilton, Ontario, using SQL, PostgreSQL, and data visualization.

The goal is to collect and analyze temperature data to identify trends, fluctuations, and unusual temperature patterns.

## Research Questions
- What time of day has the highest average temperature?
- How do temperatures change throughout the day?
- Which days experience the largest temperature fluctuations?
- How do temperature patterns change over time?

## Technologies
- PostgreSQL — Database management
- SQL — Data querying and analysis
- Python — Automated data collection (planned)
- Streamlit — Interactive dashboard (planned)
- GitHub — Version control

## Data Source
Historical weather data from Open-Meteo (planned).

## Project Timeline
- October 11–18: SQL fundamentals and database setup
- October 19–25: Data collection and analysis
- October 26–31: Dashboard development and documentation

## Future Improvements
Integrate physical temperature sensors to collect local measurements and compare them with historical weather data.

## Project Status
In development October 2026.

## Data Source

This project uses historical hourly temperature data for Hamilton, Ontario, Canada, obtained from the Open-Meteo Historical Weather API.

- Source: https://open-meteo.com/en/docs/historical-weather-api
- Location: Hamilton, Ontario
- Requested coordinates: 43.2557, -79.8711
- Weather model grid coordinates: 43.26889, -79.91031
- Date range: January 1, 2025 – December 31, 2025
- Variable: Temperature at 2 metres above ground (°C)
- Timezone: America/New_York (Eastern Time)
- File format: CSV
- Raw data file: data/hamilton_weather_2025_raw.csv

The original downloaded dataset is preserved without modification. The CSV includes metadata above the hourly temperature records.