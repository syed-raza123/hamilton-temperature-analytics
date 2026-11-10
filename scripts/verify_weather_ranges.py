
"""
Hamilton Temperature Analytics
October 21 - Task 14

Verify PostgreSQL temperature extremes
and date ranges against saved CSV files.

READ ONLY: Does not modify either database table.
"""

import os
from pathlib import Path

import pandas as pd
import psycopg
from dotenv import load_dotenv



# STEP 1: Project setup


project_root = Path(__file__).resolve().parent.parent

load_dotenv(project_root / ".env")

EXPECTED_ROWS = 8760
EXPECTED_START = pd.Timestamp("2025-01-01 00:00:00")
EXPECTED_END = pd.Timestamp("2025-12-31 23:00:00")



# STEP 2: Define both datasets

datasets = [
    {
        "name": "ORIGINAL WEATHER DATA",
        "csv": "hamilton_weather_2025_clean.csv",
        "sql": """
            SELECT
                COUNT(*),
                COUNT(DISTINCT recorded_at),
                MIN(recorded_at),
                MAX(recorded_at),
                MIN(temperature_c),
                MAX(temperature_c)
            FROM public.hamilton_weather;
        """,
        "expected_min": -19.9,
        "expected_max": 36.2
    },
    {
        "name": "API WEATHER DATA",
        "csv": "hamilton_weather_2025_api_processed.csv",
        "sql": """
            SELECT
                COUNT(*),
                COUNT(DISTINCT recorded_at),
                MIN(recorded_at),
                MAX(recorded_at),
                MIN(temperature_c),
                MAX(temperature_c)
            FROM public.hamilton_weather_api_2025;
        """,
        "expected_min": None,
        "expected_max": None
    }
]


# STEP 3: Load and validate CSV

def check_csv(filename):

    path = project_root / "data" / filename

    print("\nLoading CSV:", filename)

    if not path.exists():
        raise FileNotFoundError(
            "CSV file not found: " + str(path)
        )

    df = pd.read_csv(path)

    # Show the actual CSV column names

    print("Original CSV columns:", df.columns.tolist())

    # Remove accidental spaces and BOM characters
    # from column headers in memory only.

    df.columns = [
        str(column).strip().lstrip("\ufeff").strip()
        for column in df.columns
    ]

    # Standardize known Open Meteo column names.
    # This does NOT change the CSV file on disk.

    df = df.rename(columns={
        "time": "recorded_at",
        "temperature_2m (°C)": "temperature_c",
        "temperature_2m": "temperature_c"
    })

    print(
        "Standardized CSV columns:",
        df.columns.tolist()
    )

    # Confirm required columns are available

    expected_columns = [
        "recorded_at",
        "temperature_c"
    ]

    missing_columns = [
        column
        for column in expected_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required CSV columns in "
            + filename
            + ": "
            + str(missing_columns)
            + ". Actual columns: "
            + str(df.columns.tolist())
        )

    # Reject ambiguous duplicate column names

    if df.columns.duplicated().any():
        raise ValueError(
            "Duplicate column names detected: " + filename
        )

    # Keep only required fields for verification.
    # Other CSV columns are left untouched on disk.

    df = df[expected_columns].copy()

    # Convert timestamps

    df["recorded_at"] = pd.to_datetime(
        df["recorded_at"],
        errors="coerce"
    )

    # Convert temperatures

    df["temperature_c"] = pd.to_numeric(
        df["temperature_c"],
        errors="coerce"
    )

    # Check missing or invalid values

    if df.isna().any().any():
        raise ValueError(
            "Invalid or missing CSV values: " + filename
        )

    # Check duplicate timestamps

    if df["recorded_at"].duplicated().any():
        raise ValueError(
            "Duplicate timestamps: " + filename
        )

    # Check row count

    if len(df) != EXPECTED_ROWS:
        raise ValueError(
            "Incorrect CSV row count: " + filename
        )

    # Sort timestamps to check hourly completeness

    times = (
        df["recorded_at"]
        .sort_values()
        .reset_index(drop=True)
    )

    if (
        times.iloc[0] != EXPECTED_START
        or times.iloc[-1] != EXPECTED_END
        or not times.diff().dropna().eq(
            pd.Timedelta(hours=1)
        ).all()
    ):
        raise ValueError(
            "CSV timestamps are incomplete: " + filename
        )

    print("SUCCESS: CSV validation passed.")
    print("CSV total records:", len(df))
    print("CSV first timestamp:", times.iloc[0])
    print("CSV last timestamp:", times.iloc[-1])

    return df


# STEP 4: Verify one PostgreSQL dataset

def verify_dataset(cursor, dataset):

    print("\n" + "=" * 45)
    print(dataset["name"])
    print("=" * 45)

    # Retrieve database statistics
    # SELECT only no modifications

    cursor.execute(dataset["sql"])

    (
        total,
        unique,
        first,
        last,
        minimum,
        maximum
    ) = cursor.fetchone()

    print("\nPOSTGRESQL RESULTS")

    print("Total records:", total)
    print("Unique timestamps:", unique)
    print("First timestamp:", first)
    print("Last timestamp:", last)
    print("Minimum temperature:", minimum, "°C")
    print("Maximum temperature:", maximum, "°C")

    # Verify row counts

    if total != EXPECTED_ROWS:
        raise ValueError(
            "PostgreSQL record count mismatch."
        )

    if unique != EXPECTED_ROWS:
        raise ValueError(
            "PostgreSQL unique timestamp count mismatch."
        )

    # Verify timestamp range

    if (
        first != EXPECTED_START
        or last != EXPECTED_END
    ):
        raise ValueError(
            "PostgreSQL date range mismatch."
        )

    print(
        "SUCCESS: PostgreSQL counts and dates passed."
    )

    # Load and validate corresponding CSV

    csv_df = check_csv(dataset["csv"])

    # Calculate CSV temperature extremes

    csv_minimum = float(
        csv_df["temperature_c"].min()
    )

    csv_maximum = float(
        csv_df["temperature_c"].max()
    )

    print("\nCSV TEMPERATURE RESULTS")

    print(
        "CSV minimum temperature:",
        csv_minimum,
        "°C"
    )

    print(
        "CSV maximum temperature:",
        csv_maximum,
        "°C"
    )

    # Compare PostgreSQL extremes to its own CSV

    db_minimum = float(minimum)
    db_maximum = float(maximum)

    if (
        abs(db_minimum - csv_minimum) > 0.01
        or abs(db_maximum - csv_maximum) > 0.01
    ):
        raise ValueError(
            "PostgreSQL and CSV temperature "
            "extremes differ."
        )

    print(
        "SUCCESS: PostgreSQL matches CSV extremes."
    )

    # Verify historical original SQL results

    if dataset["expected_min"] is not None:

        expected_minimum = dataset["expected_min"]
        expected_maximum = dataset["expected_max"]

        if (
            abs(db_minimum - expected_minimum) > 0.01
            or abs(db_maximum - expected_maximum) > 0.01
        ):
            raise ValueError(
                "Original temperature extremes "
                "differ from historical SQL results."
            )

        print(
            "SUCCESS: Original SQL temperature "
            "extremes verified."
        )

    else:

        # API data is verified independently.
        # We do not force its temperatures
        # to match the original weather dataset.

        print(
            "SUCCESS: API extremes independently verified."
        )

    print(
        "SUCCESS: Dataset verification passed."
    )


# STEP 5: Connect safely to PostgreSQL

def main():

    print("TASK 14: Weather Range Verification")

    settings = {
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT", "5432"),
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD")
    }

    # Check credentials without displaying passwords

    missing_settings = [
        key
        for key, value in settings.items()
        if not value
    ]

    if missing_settings:
        raise ValueError(
            "Missing database credentials: "
            + ", ".join(missing_settings)
        )

    # Prevent connecting to the wrong database

    if settings["dbname"] != "hamilton_temperature":
        raise ValueError(
            "Unexpected database name."
        )

    # Open read only PostgreSQL connection

    with psycopg.connect(
        **settings,
        connect_timeout=5,
        options="-c default_transaction_read_only=on"
    ) as connection:

        with connection.cursor() as cursor:

            # Confirm read only mode

            cursor.execute(
                "SHOW transaction_read_only;"
            )

            read_only = cursor.fetchone()[0]

            if read_only != "on":
                raise ValueError(
                    "Connection is not read-only."
                )

            print(
                "SUCCESS: Read-only database connection."
            )

            # Verify original and API datasets separately

            for dataset in datasets:

                verify_dataset(
                    cursor,
                    dataset
                )

    # Final success message

    print("\n" + "=" * 45)

    print(
        "SUCCESS: TASK 14 ALL CHECKS PASSED!"
    )

    print(
        "Both datasets verified independently."
    )

    print(
        "No database records were modified."
    )



# STEP 6: 

if __name__ == "__main__":

    try:

        main()

    except (
        psycopg.Error,
        OSError,
        ValueError,
        TypeError
    ) as error:

        print(
            "\nERROR: Task 14 verification failed."
        )

        print("Error:", error)

        raise SystemExit(1) from error
