# hamilton-temperature-analytics
SQL-based temperature analytics project
# Hamilton Temperature Analytics

## Project Overview
This project analyzes hourly temperature data from Hamilton, Ontario, throughout 2025 using PostgreSQL and SQL. The dataset contains 8,760 hourly temperature readings, allowing for an examination of daily temperature patterns, seasonal trends, extreme weather conditions, and temperature fluctuations.

The goal of this project is to demonstrate practical SQL skills, including data validation, filtering, aggregation, grouping, and time-based analysis, while using real-world weather data to identify meaningful patterns and insights.

## Key Findings
1. The hottest hour and hottest day were different

The highest hourly temperature was 36.2°C, recorded on June 23, 2025, at 16:00. However, the highest daily average temperature was 30.28°C on June 24, 2025. This demonstrates that a single temperature peak does not necessarily occur on the day with the highest overall average.

2. Hamilton experienced substantial temperature extremes

Throughout 2025, Hamilton recorded 165 hours above 30°C and 2,285 hours below 0°C. These findings highlight the contrast between hot summer conditions and prolonged below-freezing conditions during colder months.

3. Afternoons were warmer than mornings

The average afternoon temperature was 11.76°C, compared with 7.60°C in the morning. Afternoons were therefore approximately 4.16°C warmer, on average, across the observation periods used in the analysis.


## Research Questions
- What time of day has the highest average temperature?
- How do temperatures change throughout the day?
- Which days experience the largest temperature fluctuations?
- How do temperature patterns change over time?

## Technologies
- **PostgreSQL:** Relational database management
  system used to store and analyze the dataset.
- **SQL:** Used for data validation, filtering,
  aggregation, grouping, and time-based analysis.
- **pgAdmin 4:** Used to execute SQL queries
  and inspect database results.
- **Visual Studio Code:** Used to write and
  organize SQL scripts and documentation.
- **Git and GitHub:** Used for version control
  and hosting the project repository.
- **GitHub Desktop:** Used to commit and push
  project updates.
- **Open-Meteo:** Source of the historical
  hourly temperature dataset.

## Data Import Process
\copy public.hamilton_weather
(recorded_at, temperature_c)
FROM '/path/to/cleaned.csv'
WITH (FORMAT csv, HEADER true);


## Database Structure

The project uses a PostgreSQL table named
`hamilton_weather`, containing 8,760 hourly
temperature records from 2025.

| Column | Description |
|---|---|
| recorded_at | Date and time of the observation |
| temperature_c | Temperature in degrees Celsius |

The dataset contains 8,760 unique timestamps
with no missing temperature values.
## Project Timeline
- October 11–18: SQL fundamentals and database setup
- October 19–25: Data collection and analysis
- October 26–31: Dashboard development and documentation

## Future Improvements
Integrate physical temperature sensors to collect local measurements and compare them with historical weather data.

## Project Status
In development October 2026.

## Data Source
The dataset was obtained from
[Open-Meteo](https://open-meteo.com/),
using its historical weather data service.

- **Location:** Hamilton, Ontario, Canada
- **Coordinates:** Approximately 43.27°N, 79.91°W
- **Time period:** January 1 – December 31, 2025
- **Frequency:** Hourly
- **Temperature unit:** Degrees Celsius (°C)
- **Total records:** 8,760

The historical weather data was downloaded
as a CSV file and subsequently imported
into PostgreSQL for validation and SQL
analysis.