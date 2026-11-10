
"""
Hamilton Temperature Analytics
October 21 - Task 11

Post-load database reconciliation.

Compare saved API CSV data with the
separate PostgreSQL API weather table.

READ ONLY: Does not modify database records.
"""

import os
from pathlib import Path

import pandas as pd
import psycopg
from dotenv import load_dotenv


# STEP 1: Locate the project

project_root = Path(__file__).resolve().parent.parent

load_dotenv(project_root / ".env")

csv_path = (
    project_root
    / "data"
    / "hamilton_weather_2025_api_processed.csv"
)

print("TASK 11: Post-Load Data Reconciliation")

try:
    # STEP 2: Load the saved API CSV

    csv_df = pd.read_csv(csv_path)

    expected_columns = ["recorded_at", "temperature_c"]

    if csv_df.columns.tolist() != expected_columns:
        raise ValueError("Unexpected CSV columns.")

    csv_df["recorded_at"] = pd.to_datetime(
        csv_df["recorded_at"],
        errors="coerce"
    )

    csv_df["temperature_c"] = pd.to_numeric(
        csv_df["temperature_c"],
        errors="coerce"
    )

    if len(csv_df) != 8760:
        raise ValueError("CSV row count is incorrect.")

    if csv_df.isna().any().any():
        raise ValueError("Invalid CSV values detected.")

    if csv_df["recorded_at"].duplicated().any():
        raise ValueError("Duplicate CSV timestamps detected.")

    if not csv_df["temperature_c"].between(
        -100, 100
    ).all():
        raise ValueError("Invalid temperature values.")

    print("CSV records:", len(csv_df))

    # STEP 3: Load database credentials

    credentials = {
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT", "5432"),
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD")
    }

    missing = [
        key
        for key, value in credentials.items()
        if not value
    ]

    if missing:
        raise ValueError(
            "Missing database connection settings."
        )

    # STEP 4: Connect to PostgreSQL (READ ONLY)

    with psycopg.connect(
        **credentials,
        connect_timeout=5,
        options="-c default_transaction_read_only=on"
    ) as connection:

        with connection.cursor() as cursor:

            # Confirm read-only transaction mode

            cursor.execute("SHOW transaction_read_only;")

            if cursor.fetchone()[0] != "on":
                raise ValueError(
                    "Database connection is not read-only."
                )

            print("SUCCESS: Read-only PostgreSQL connection.")

            # STEP 5: Retrieve API table records

            cursor.execute("""
                SELECT
                    recorded_at,
                    temperature_c
                FROM public.hamilton_weather_api_2025
                ORDER BY recorded_at;
            """)

            database_rows = cursor.fetchall()

            # Verify the original table's summary

            cursor.execute("""
                SELECT
                    COUNT(*),
                    COUNT(DISTINCT recorded_at),
                    MIN(temperature_c),
                    MAX(temperature_c)
                FROM public.hamilton_weather;
            """)

            original_stats = cursor.fetchone()

    # STEP 6: Convert database rows to DataFrame

    db_df = pd.DataFrame(
        database_rows,
        columns=expected_columns
    )

    db_df["recorded_at"] = pd.to_datetime(
        db_df["recorded_at"],
        errors="coerce"
    )

    db_df["temperature_c"] = pd.to_numeric(
        db_df["temperature_c"],
        errors="coerce"
    )

    if db_df.isna().any().any():
        raise ValueError("Invalid database values.")

    if db_df["recorded_at"].duplicated().any():
        raise ValueError("Duplicate database timestamps.")

    print("Database API records:", len(db_df))

    # STEP 7: Match records by timestamp

    comparison = csv_df.merge(
        db_df,
        on="recorded_at",
        how="outer",
        suffixes=("_csv", "_db"),
        indicator=True,
        validate="one_to_one"
    )

    # Count matching and nonmatching timestamps

    matched_count = (
        comparison["_merge"] == "both"
    ).sum()

    missing_count = (
        comparison["_merge"] == "left_only"
    ).sum()

    extra_count = (
        comparison["_merge"] == "right_only"
    ).sum()

    # STEP 8: Compare matching temperatures

    matched_df = comparison[
        comparison["_merge"] == "both"
    ].copy()

    matched_df["temperature_difference"] = (
        matched_df["temperature_c_csv"]
        - matched_df["temperature_c_db"]
    ).abs()

    mismatches = matched_df[
        matched_df["temperature_difference"] > 0.01
    ]

    mismatch_count = len(mismatches)

    print("\nRECONCILIATION RESULTS")

    print("Matching timestamps:", matched_count)
    print("Missing database timestamps:", missing_count)
    print("Extra database timestamps:", extra_count)
    print("Temperature mismatches:", mismatch_count)

    # STEP 9: Report discrepancies

    if mismatch_count > 0:
        print("\nFirst 5 temperature mismatches:")
        print(
            mismatches[
                [
                    "recorded_at",
                    "temperature_c_csv",
                    "temperature_c_db",
                    "temperature_difference"
                ]
            ].head()
        )

    # STEP 10: Verify original table summary

    original_valid = (
        original_stats[0] == 8760
        and original_stats[1] == 8760
        and float(original_stats[2]) == -19.9
        and float(original_stats[3]) == 36.2
    )

    # STEP 11: Final reconciliation check

    if (
        len(csv_df) == 8760
        and len(db_df) == 8760
        and matched_count == 8760
        and missing_count == 0
        and extra_count == 0
        and mismatch_count == 0
        and original_valid
    ):
        print("\nSUCCESS: All reconciliation checks passed!")
        print("Original table safety checks passed.")
        print("Database records match the saved API CSV.")

    else:
        raise ValueError(
            "Reconciliation failed. Investigate differences."
        )

except (OSError, ValueError, psycopg.Error) as error:
    print("\nERROR: Reconciliation unsuccessful.")
    print("Error type:", type(error).__name__)
    raise SystemExit(1) from error
