
"""
Hamilton Temperature Analytics
October 21 - Task 7

Validate timestamp and temperature data types
before PostgreSQL loading.

This script does not modify any files or databases.
"""

from pathlib import Path
import pandas as pd
import numpy as np


# Locate the project folder
project_root = Path(__file__).resolve().parent.parent

# Locate the processed API CSV
csv_path = (
    project_root
    / "data"
    / "hamilton_weather_2025_api_processed.csv"
)

print("TASK 7: Weather Data Type Validation")

try:
    # STEP 1: Load the processed API dataset
    df = pd.read_csv(csv_path)

    print("\nRows loaded:", len(df))

    print("\nOriginal data types:")
    print(df.dtypes)

    # STEP 2: Check required columns
    expected_columns = [
        "recorded_at",
        "temperature_c"
    ]

    if df.columns.tolist() != expected_columns:
        raise ValueError(
            "CSV columns do not match the expected structure."
        )

    # STEP 3: Convert timestamps to datetime
    df["recorded_at"] = pd.to_datetime(
        df["recorded_at"],
        errors="coerce"
    )

    # STEP 4: Convert temperatures to numeric
    df["temperature_c"] = pd.to_numeric(
        df["temperature_c"],
        errors="coerce"
    )

    print("\nData types after conversion:")
    print(df.dtypes)

    # STEP 5: Count invalid values
    invalid_timestamps = df["recorded_at"].isna().sum()
    invalid_temperatures = df["temperature_c"].isna().sum()

    print("\nInvalid timestamps:", invalid_timestamps)
    print("Invalid temperatures:", invalid_temperatures)

    # STEP 6: Check for duplicate timestamps
    duplicate_count = df.duplicated(
        subset=["recorded_at"]
    ).sum()

    print("Duplicate timestamps:", duplicate_count)

    # STEP 7: Check for finite temperature values
    finite_temperatures = np.isfinite(
        df["temperature_c"].dropna().to_numpy(dtype=float)
    ).all()

    # STEP 8: Validate expected date range
    expected_start = pd.Timestamp("2025-01-01 00:00:00")
    expected_end = pd.Timestamp("2025-12-31 23:00:00")

    date_range_valid = (
        df["recorded_at"].min() == expected_start
        and df["recorded_at"].max() == expected_end
    )

    # STEP 9: Final validation
    if (
        len(df) == 8760
        and invalid_timestamps == 0
        and invalid_temperatures == 0
        and duplicate_count == 0
        and finite_temperatures
        and date_range_valid
    ):
        print("\nSUCCESS: All validation checks passed!")

        # Convert a sample row to native Python types
        sample_timestamp = (
            df.iloc[0]["recorded_at"].to_pydatetime()
        )

        sample_temperature = float(
            df.iloc[0]["temperature_c"]
        )

        print("\nSample PostgreSQL-ready values:")
        print("Timestamp:", sample_timestamp)
        print("Temperature:", sample_temperature)

        print("\nNative Python types:")
        print("Timestamp:", type(sample_timestamp).__name__)
        print("Temperature:", type(sample_temperature).__name__)

        print("\nDataset is ready for the next pipeline steps.")

    else:
        print("\nWARNING: Data validation failed.")
        print("Do not load this dataset into PostgreSQL.")

except (OSError, ValueError, pd.errors.ParserError) as error:
    print("\nERROR: Could not validate weather data.")
    print("Error type:", type(error).__name__)
    print("Details:", error)
