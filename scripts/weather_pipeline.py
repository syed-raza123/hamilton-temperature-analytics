
"""
Hamilton Temperature Analytics
Weather Data Pipeline

October 21 - Tasks 10, 11, and 13

Extract, validate, load, reconcile, and log
Hamilton's 2025 hourly weather data.

The original database table is read-only.
"""

import os
from pathlib import Path

import pandas as pd
import psycopg
import requests
from dotenv import load_dotenv
from pipeline_logger import get_logger


# SETUP: Paths, credentials, and logging

PROJECT_ROOT = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_ROOT / ".env")

logger = get_logger()

API_URL = "https://archive-api.open-meteo.com/v1/archive"

API_PARAMS = {
    "latitude": 43.27,
    "longitude": -79.91,
    "start_date": "2025-01-01",
    "end_date": "2025-12-31",
    "hourly": "temperature_2m",
    "temperature_unit": "celsius",
    "timezone": "America/Toronto",
}

START = pd.Timestamp("2025-01-01 00:00:00")
END = pd.Timestamp("2025-12-31 23:00:00")
EXPECTED_ROWS = 8760


# DATABASE CONNECTION SETTINGS

def connection_settings():

    settings = {
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT", "5432"),
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
    }

    missing = [
        key
        for key, value in settings.items()
        if not value
    ]

    if missing:
        raise ValueError(
            "Missing database settings: "
            + ", ".join(missing)
        )

    if settings["dbname"] != "hamilton_temperature":
        raise ValueError(
            "Unexpected database name. Stopping for safety."
        )

    return settings


# STEP 1: VALIDATE FRESH API DATA

def validate_api(df):

    if df.columns.tolist() != [
        "recorded_at",
        "temperature_c"
    ]:
        raise ValueError("Unexpected API columns.")

    df = df.copy()

    df["recorded_at"] = pd.to_datetime(
        df["recorded_at"],
        errors="coerce"
    )

    df["temperature_c"] = pd.to_numeric(
        df["temperature_c"],
        errors="coerce"
    )

    if len(df) != EXPECTED_ROWS:
        raise ValueError("Unexpected API row count.")

    if df.isna().any().any():
        raise ValueError("Missing or invalid API values.")

    if df["recorded_at"].duplicated().any():
        raise ValueError(
            "Duplicate API timestamps detected."
        )

    if not df["temperature_c"].between(
        -100, 100
    ).all():
        raise ValueError(
            "API temperatures outside the safe range."
        )

    df = df.sort_values(
        "recorded_at"
    ).reset_index(drop=True)

    times = df["recorded_at"]

    if (
        times.iloc[0] != START
        or times.iloc[-1] != END
        or not times.diff().dropna().eq(
            pd.Timedelta(hours=1)
        ).all()
    ):
        raise ValueError(
            "API timestamps are not a complete "
            "hourly 2025 series."
        )

    print("SUCCESS: API validation passed.")
    print("Validated records:", len(df))

    logger.info(
        "API validation passed: %d records, "
        "no missing or duplicate hours.",
        len(df)
    )

    return df


# STEP 2: COMPARE WITH ORIGINAL CSV
# READ-ONLY COMPARISON

def compare_with_original_csv(api_df):

    original_path = (
        PROJECT_ROOT
        / "data"
        / "hamilton_weather_2025_clean.csv"
    )

    if not original_path.exists():
        raise ValueError(
            "Original CSV missing. Import blocked."
        )

    original_df = pd.read_csv(original_path)

    original_df = original_df.rename(columns={
        "time": "recorded_at",
        "temperature_2m (°C)": "temperature_c",
    })

    if not {
        "recorded_at",
        "temperature_c"
    }.issubset(original_df.columns):
        raise ValueError(
            "Original CSV has unexpected columns."
        )

    original_df["recorded_at"] = pd.to_datetime(
        original_df["recorded_at"]
    )

    original_df["temperature_c"] = pd.to_numeric(
        original_df["temperature_c"],
        errors="coerce"
    )

    comparison = original_df.merge(
        api_df,
        on="recorded_at",
        how="outer",
        suffixes=("_original", "_api"),
        indicator=True,
        validate="one_to_one",
    )

    matched = comparison.loc[
        comparison["_merge"] == "both"
    ].copy()

    differences = (
        matched["temperature_c_original"]
        - matched["temperature_c_api"]
    ).abs()

    mismatch_count = int(
        (differences > 0.01).sum()
    )

    print("\nORIGINAL CSV COMPARISON")

    print("Original CSV rows:", len(original_df))
    print("API rows:", len(api_df))
    print("Matching timestamps:", len(matched))
    print(
        "Temperature differences > 0.01°C:",
        mismatch_count
    )

    if len(matched) != EXPECTED_ROWS:
        raise ValueError(
            "Original CSV timestamps do not match "
            "the API timestamps."
        )

    if mismatch_count:

        print(
            "WARNING: Original CSV and API "
            "temperatures differ, as previously observed."
        )

        logger.warning(
            "Original CSV differs from API in "
            "%d readings; datasets remain separate.",
            mismatch_count
        )

    else:

        logger.info(
            "Original CSV and API temperatures "
            "agree within 0.01°C."
        )


# STEP 3: SAVE API CSV WITHOUT OVERWRITING

def save_api_csv_without_overwriting(api_df):

    output = (
        PROJECT_ROOT
        / "data"
        / "hamilton_weather_2025_api_processed.csv"
    )

    if output.exists():

        print(
            "\nProcessed API CSV already exists; "
            "it was not overwritten."
        )

        logger.info(
            "Existing API CSV preserved "
            "without overwriting."
        )

    else:

        api_df.to_csv(
            output,
            index=False
        )

        print(
            "\nProcessed API CSV saved to:",
            output
        )

        logger.info("Separate API CSV created.")

    saved = pd.read_csv(output)

    print("Saved API CSV rows:", len(saved))

    if len(saved) != EXPECTED_ROWS:
        raise ValueError(
            "Saved API CSV contains an unexpected "
            "number of rows."
        )


# STEP 4: ORIGINAL POSTGRESQL SAFETY CHECK
# READ-ONLY QUERY

def original_stats(cursor):

    cursor.execute("""
        SELECT
            COUNT(*),
            COUNT(DISTINCT recorded_at),
            MIN(temperature_c),
            MAX(temperature_c)
        FROM public.hamilton_weather;
    """)

    stats = cursor.fetchone()

    if (
        stats[0] != EXPECTED_ROWS
        or stats[1] != EXPECTED_ROWS
        or float(stats[2]) != -19.9
        or float(stats[3]) != 36.2
    ):
        raise ValueError(
            "Original PostgreSQL table "
            "failed safety checks."
        )

    return stats


# STEP 5: TASK 11 - RECONCILE FRESH API DATA

def reconcile_fresh_api(
    api_df,
    database_rows
):

    db_df = pd.DataFrame(
        database_rows,
        columns=[
            "recorded_at",
            "temperature_c"
        ]
    )

    db_df["recorded_at"] = pd.to_datetime(
        db_df["recorded_at"],
        errors="coerce"
    )

    db_df["temperature_c"] = pd.to_numeric(
        db_df["temperature_c"],
        errors="coerce"
    )

    if (
        db_df.isna().any().any()
        or db_df["recorded_at"].duplicated().any()
    ):
        raise ValueError(
            "API database contains invalid values "
            "or duplicate timestamps."
        )

    compared = api_df.merge(
        db_df,
        on="recorded_at",
        how="outer",
        suffixes=("_api", "_db"),
        indicator=True,
        validate="one_to_one",
    )

    matching = (
        compared["_merge"] == "both"
    )

    missing = int(
        (
            compared["_merge"] == "left_only"
        ).sum()
    )

    extra = int(
        (
            compared["_merge"] == "right_only"
        ).sum()
    )

    matched = compared.loc[
        matching
    ].copy()

    matched["difference"] = (
        matched["temperature_c_api"]
        - matched["temperature_c_db"]
    ).abs()

    mismatched = matched[
        matched["difference"] > 0.01
    ]

    print(
        "\nTASK 11: Post-Load Data Reconciliation"
    )

    print("Fresh API records:", len(api_df))
    print("Database API records:", len(db_df))
    print("Matching timestamps:", len(matched))
    print("Missing database timestamps:", missing)
    print("Extra database timestamps:", extra)

    print(
        "Temperature mismatches > 0.01°C:",
        len(mismatched)
    )

    if len(mismatched):

        print("First five mismatches:")

        print(
            mismatched[
                [
                    "recorded_at",
                    "temperature_c_api",
                    "temperature_c_db",
                    "difference"
                ]
            ].head()
        )

    if (
        len(db_df) != EXPECTED_ROWS
        or len(matched) != EXPECTED_ROWS
        or missing != 0
        or extra != 0
        or len(mismatched) != 0
    ):
        raise ValueError(
            "Reconciliation failed; database "
            "transaction will roll back."
        )

    print(
        "SUCCESS: All reconciliation checks passed."
    )

    logger.info(
        "Reconciliation passed: %d matching, "
        "0 missing, 0 extra, 0 mismatches.",
        len(matched)
    )


# STEP 6: MAIN WEATHER PIPELINE

def main():

    # TASK 13: START LOGGING

    logger.info("Weather pipeline started.")

    print(
        "OCTOBER 21: Integrated weather pipeline "
        "with Task 13 logging"
    )

    # EXTRACT DATA FROM OPEN METEO

    response = requests.get(
        API_URL,
        params=API_PARAMS,
        timeout=60
    )

    response.raise_for_status()

    data = response.json()["hourly"]

    df = pd.DataFrame({
        "recorded_at": data["time"],
        "temperature_c": data["temperature_2m"],
    })

    logger.info(
        "Open-Meteo API extraction succeeded: "
        "%d rows received.",
        len(df)
    )

    print("\nFirst five API readings:")
    print(df.head())

    # VALIDATE DATA

    api_df = validate_api(df)

    # COMPARE WITHOUT MODIFYING ORIGINAL CSV

    compare_with_original_csv(api_df)

    # PRESERVE EXISTING API CSV

    save_api_csv_without_overwriting(api_df)

    # LOAD DATABASE SETTINGS

    settings = connection_settings()

    # READ ONLY POSTGRESQL CONNECTION

    print(
        "\nTASK 4: Read-Only PostgreSQL Connection"
    )

    with psycopg.connect(
        **settings,
        connect_timeout=5,
        options="-c default_transaction_read_only=on"
    ) as connection:

        with connection.cursor() as cursor:

            cursor.execute(
                "SHOW transaction_read_only;"
            )

            if cursor.fetchone()[0] != "on":
                raise ValueError(
                    "Expected a read-only database connection."
                )

            original_stats(cursor)

    print(
        "SUCCESS: Original PostgreSQL data "
        "matches expected results."
    )

    logger.info(
        "Read-only original PostgreSQL "
        "verification passed."
    )

    # TASK 10: SAFE API DATABASE LOADING

    print(
        "\nTASK 10: Automated PostgreSQL Pipeline"
    )

    records = [
        (
            timestamp.to_pydatetime(),
            float(temperature)
        )
        for timestamp, temperature
        in api_df.itertuples(
            index=False,
            name=None
        )
    ]

    # Only this connection inserts records.
    # All INSERT statements target the API table.

    with psycopg.connect(
        **settings,
        connect_timeout=5
    ) as connection:

        with connection.cursor() as cursor:

            before_original = original_stats(
                cursor
            )

            print(
                "SUCCESS: Original table safety "
                "check passed."
            )

            # Confirm the separate API table exists

            cursor.execute("""
                SELECT to_regclass(
                    'public.hamilton_weather_api_2025'
                );
            """)

            if cursor.fetchone()[0] is None:
                raise ValueError(
                    "Separate API table is missing. "
                    "Complete Task 9 setup first."
                )

            # Count existing API records

            cursor.execute("""
                SELECT COUNT(*)
                FROM public.hamilton_weather_api_2025;
            """)

            before_count = cursor.fetchone()[0]

            print(
                "API table rows before:",
                before_count
            )

            # Insert only timestamps not already stored

            cursor.executemany("""
                INSERT INTO public.hamilton_weather_api_2025 (
                    recorded_at,
                    temperature_c
                )
                VALUES (%s, %s)
                ON CONFLICT (recorded_at) DO NOTHING;
            """, records)

            inserted = cursor.rowcount

            print(
                "New records inserted:",
                inserted
            )

            logger.info(
                "PostgreSQL API loading: %d rows "
                "previously present, %d inserted.",
                before_count,
                inserted
            )

            # Validate API table statistics

            cursor.execute("""
                SELECT
                    COUNT(*),
                    COUNT(DISTINCT recorded_at),
                    MIN(recorded_at),
                    MAX(recorded_at)
                FROM public.hamilton_weather_api_2025;
            """)

            (
                count,
                unique_count,
                first,
                last
            ) = cursor.fetchone()

            print("\nAPI TABLE VALIDATION")

            print("Total records:", count)
            print("Unique timestamps:", unique_count)
            print("First timestamp:", first)
            print("Last timestamp:", last)

            if (
                count != EXPECTED_ROWS
                or unique_count != EXPECTED_ROWS
                or first != START
                or last != END
            ):
                raise ValueError(
                    "API table validation failed; "
                    "transaction will roll back."
                )

            # Verify original table was not changed

            if original_stats(cursor) != before_original:
                raise ValueError(
                    "Original weather table "
                    "safety check failed."
                )

            print(
                "SUCCESS: Original table checks unchanged."
            )

            logger.info(
                "Original table unchanged according "
                "to recorded safety checks."
            )

            # TASK 11: POST LOAD RECONCILIATION

            cursor.execute("""
                SELECT
                    recorded_at,
                    temperature_c
                FROM public.hamilton_weather_api_2025
                ORDER BY recorded_at;
            """)

            reconcile_fresh_api(
                api_df,
                cursor.fetchall()
            )

    # The transaction commits only after all checks pass

    print(
        "\nSUCCESS: Task 10 pipeline completed."
    )

    print(
        "SUCCESS: Task 11 reconciliation completed."
    )

    print(
        "SUCCESS: Task 13 pipeline logging completed."
    )

    logger.info(
        "Weather pipeline completed successfully; "
        "database transaction committed."
    )


# STEP 7: TASK 13 LOG ERRORS SAFELY

if __name__ == "__main__":

    try:
        main()

    except (
        requests.exceptions.RequestException,
        psycopg.Error,
        pd.errors.ParserError,
        OSError,
        KeyError,
        TypeError,
        ValueError
    ) as error:

        print(
            "ERROR: Pipeline failed:",
            type(error).__name__
        )

        # Log error type, never the DB password

        logger.error(
            "Pipeline failed: %s.",
            type(error).__name__
        )

        raise SystemExit(1) from error
