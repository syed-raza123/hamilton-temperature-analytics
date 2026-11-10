
"""
Hamilton Temperature Analytics
October 21 - Task 12

Test PostgreSQL transaction rollback safely.

Uses only a temporary practice table.
Does not modify original or API weather data.
"""

import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv


# STEP 1: Load database credentials

project_root = Path(__file__).resolve().parent.parent

load_dotenv(project_root / ".env")

credentials = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT", "5432"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD")
}

print("TASK 12: PostgreSQL Transaction Rollback")

missing = [
    key
    for key, value in credentials.items()
    if not value
]

if missing:
    raise SystemExit(
        "Missing database settings: " + ", ".join(missing)
    )


try:
    # STEP 2: Connect to PostgreSQL

    # Autocommit is enabled outside explicit transactions.
    # The practice INSERT still happens inside a transaction.

    with psycopg.connect(
        **credentials,
        connect_timeout=5,
        autocommit=True
    ) as connection:

        with connection.cursor() as cursor:

            cursor.execute("SELECT current_database();")

            database_name = cursor.fetchone()[0]

            if database_name != "hamilton_temperature":
                raise ValueError(
                    "Connected to an unexpected database."
                )

            print("SUCCESS: Connected to PostgreSQL.")

            # STEP 3: Record original table counts

            cursor.execute("""
                SELECT COUNT(*)
                FROM public.hamilton_weather;
            """)

            original_before = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COUNT(*)
                FROM public.hamilton_weather_api_2025;
            """)

            api_before = cursor.fetchone()[0]

            print("Original table rows before:", original_before)
            print("API table rows before:", api_before)

            # STEP 4: Begin a controlled test transaction

            try:
                with connection.transaction():

                    # Create a temporary practice table

                    cursor.execute("""
                        CREATE TEMP TABLE task12_rollback_demo (
                            reading_id INTEGER PRIMARY KEY,
                            temperature_c NUMERIC NOT NULL
                        ) ON COMMIT DROP;
                    """)

                    # Insert a single practice record

                    cursor.execute("""
                        INSERT INTO task12_rollback_demo (
                            reading_id,
                            temperature_c
                        )
                        VALUES (%s, %s);
                    """, (1, 2.2))

                    cursor.execute("""
                        SELECT COUNT(*)
                        FROM task12_rollback_demo;
                    """)

                    practice_count = cursor.fetchone()[0]

                    print(
                        "Temporary practice rows:",
                        practice_count
                    )

                    if practice_count != 1:
                        raise ValueError(
                            "Practice insertion failed."
                        )

                    # STEP 5: Simulate a failure

                    print("\nSimulating a transaction failure...")

                    raise RuntimeError(
                        "Intentional rollback test"
                    )

            except RuntimeError:
                print("Expected test error detected.")
                print("Transaction rolled back.")

            # STEP 6: Verify the temporary table
            # was removed by the rollback

            cursor.execute("""
                SELECT to_regclass(
                    'pg_temp.task12_rollback_demo'
                );
            """)

            remaining_table = cursor.fetchone()[0]

            if remaining_table is not None:
                raise ValueError(
                    "Rollback verification failed."
                )

            print(
                "SUCCESS: Temporary table was rolled back."
            )

            # STEP 7: Verify both weather tables

            cursor.execute("""
                SELECT COUNT(*)
                FROM public.hamilton_weather;
            """)

            original_after = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COUNT(*)
                FROM public.hamilton_weather_api_2025;
            """)

            api_after = cursor.fetchone()[0]

            print("\nDATABASE SAFETY CHECK")

            print("Original table rows after:", original_after)
            print("API table rows after:", api_after)

            if (
                original_before != original_after
                or api_before != api_after
            ):
                raise ValueError(
                    "Weather table row counts changed."
                )

            if original_after != 8760 or api_after != 8760:
                raise ValueError(
                    "Unexpected weather table row count."
                )

            print(
                "SUCCESS: Both weather tables remain intact."
            )

    print("\nSUCCESS: Task 12 rollback test passed!")

except (psycopg.Error, ValueError, OSError) as error:
    print("\nERROR: Rollback test failed.")
    print("Error type:", type(error).__name__)
    raise SystemExit(1) from error
