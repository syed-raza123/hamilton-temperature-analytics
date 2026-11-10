"""
Hamilton Temperature Analytics - Task 9
Safe, repeatable import of the saved 2025 API CSV to PostgreSQL.

This script does not change the original weather CSV or SQL table.
"""

import os
from pathlib import Path

import pandas as pd
import psycopg
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "data" / "hamilton_weather_2025_api_processed.csv"
load_dotenv(ROOT / ".env")

EXPECTED_START = pd.Timestamp("2025-01-01 00:00:00")
EXPECTED_END = pd.Timestamp("2025-12-31 23:00:00")
EXPECTED_ROWS = 8760


def load_and_validate_csv():
    if not CSV_PATH.is_file():
        raise FileNotFoundError(f"API CSV not found: {CSV_PATH}")

    df = pd.read_csv(CSV_PATH)
    if df.columns.tolist() != ["recorded_at", "temperature_c"]:
        raise ValueError(f"Unexpected API CSV columns: {df.columns.tolist()}")

    df["recorded_at"] = pd.to_datetime(df["recorded_at"], errors="coerce")
    df["temperature_c"] = pd.to_numeric(df["temperature_c"], errors="coerce")

    if df.isna().any().any():
        raise ValueError("API CSV contains missing or invalid values.")
    if df["recorded_at"].duplicated().any():
        raise ValueError("API CSV contains duplicate timestamps.")
    if len(df) != EXPECTED_ROWS:
        raise ValueError(f"Expected {EXPECTED_ROWS} rows, found {len(df)}.")

    actual_hours = df["recorded_at"].sort_values().reset_index(drop=True)
    expected_hours = pd.date_range(EXPECTED_START, EXPECTED_END, freq="h")
    if actual_hours.tolist() != list(expected_hours):
        raise ValueError("API CSV does not contain every hour of 2025 exactly once.")

    print("SUCCESS: CSV validation passed.")
    print("Validated records:", len(df))
    return [
        (pd.Timestamp(timestamp).to_pydatetime(), float(temperature))
        for timestamp, temperature in df.itertuples(index=False, name=None)
    ]


def original_stats(cursor):
    cursor.execute("""
        SELECT COUNT(*), MIN(recorded_at), MAX(recorded_at),
               MIN(temperature_c), MAX(temperature_c)
        FROM public.hamilton_weather;
    """)
    return cursor.fetchone()


def verify_original(stats):
    count, first, last, minimum, maximum = stats
    if not (
        count == EXPECTED_ROWS
        and first == EXPECTED_START
        and last == EXPECTED_END
        and abs(float(minimum) - (-19.9)) <= 0.01
        and abs(float(maximum) - 36.2) <= 0.01
    ):
        raise ValueError("Original weather table failed its safety checks.")


def main():
    print("TASK 9: Safe PostgreSQL API Data Import")
    rows = load_and_validate_csv()

    settings = {
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT", "5432"),
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
    }
    if any(not value for value in settings.values()):
        raise ValueError("Database credentials are missing from .env.")
    if settings["dbname"] != "hamilton_temperature":
        raise ValueError("Unexpected database name; import cancelled.")

    # The connection transaction commits only if every check succeeds.
    # Otherwise psycopg rolls back the transaction automatically.
    with psycopg.connect(**settings, connect_timeout=5) as connection:
        with connection.cursor() as cursor:
            print("SUCCESS: Connected to PostgreSQL.")
            original_before = original_stats(cursor)
            verify_original(original_before)

            # Create ONLY the separate API table, if it is missing.
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS public.hamilton_weather_api_2025 (
                    recorded_at TIMESTAMP WITHOUT TIME ZONE PRIMARY KEY,
                    temperature_c NUMERIC NOT NULL
                );
            """)
            cursor.execute("SELECT COUNT(*) FROM public.hamilton_weather_api_2025;")
            rows_before = cursor.fetchone()[0]
            print("API table rows before:", rows_before)

            # %s placeholders prevent SQL injection ON CONFLICT
            # makes repeated imports safe from duplicate timestamps.
            cursor.executemany("""
                INSERT INTO public.hamilton_weather_api_2025
                    (recorded_at, temperature_c)
                VALUES (%s, %s)
                ON CONFLICT (recorded_at) DO NOTHING;
            """, rows)

            cursor.execute("""
                SELECT COUNT(*), COUNT(DISTINCT recorded_at),
                       MIN(recorded_at), MAX(recorded_at)
                FROM public.hamilton_weather_api_2025;
            """)
            total, unique, first, last = cursor.fetchone()
            inserted = total - rows_before

            print("New records inserted:", inserted)
            print("\nAPI TABLE VALIDATION")
            print("Total records:", total)
            print("Unique timestamps:", unique)
            print("First timestamp:", first)
            print("Last timestamp:", last)

            if not (
                total == EXPECTED_ROWS
                and unique == EXPECTED_ROWS
                and first == EXPECTED_START
                and last == EXPECTED_END
            ):
                raise ValueError("API table count or date range failed verification.")

            # Ensure each API table temperature matches the saved API CSV.
            cursor.execute("""
                SELECT recorded_at, temperature_c
                FROM public.hamilton_weather_api_2025;
            """)
            stored = {timestamp: float(temp) for timestamp, temp in cursor.fetchall()}
            if any(
                timestamp not in stored or abs(stored[timestamp] - temp) > 0.01
                for timestamp, temp in rows
            ):
                raise ValueError("API table temperatures differ from the saved API CSV.")

            original_after = original_stats(cursor)
            verify_original(original_after)
            if original_before != original_after:
                raise ValueError("Original table safety statistics changed.")

            print("SUCCESS: API table validation passed.")
            print("Original table records:", original_after[0])

    print("\nSUCCESS: Import transaction completed.")


if __name__ == "__main__":
    try:
        main()
    except (psycopg.Error, OSError, ValueError, TypeError) as error:
        print("\nERROR: API import cancelled; uncommitted changes rolled back.")
        print("Error:", error)
        raise SystemExit(1) from error
