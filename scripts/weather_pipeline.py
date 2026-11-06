
"""
Hamilton Temperature Analytics
Weather data pipeline

This script will retrieve, process, and store
Hamilton weather data.
"""

from pathlib import Path

import requests
import pandas as pd

url = "https://archive-api.open-meteo.com/v1/archive"

params = {
    "latitude": 43.27,
    "longitude": -79.91,
    "start_date": "2025-01-01",
    "end_date": "2025-12-31",
    "hourly": "temperature_2m",
    "temperature_unit": "celsius",
    "timezone": "America/Toronto"
}

try:
    response = requests.get(url, params=params, timeout=60)
    response.raise_for_status()

    data = response.json()

    timestamps = data["hourly"]["time"]
    temperatures = data["hourly"]["temperature_2m"]

    print("First 5 timestamps:", timestamps[:5])
    print("First 5 temperatures:", temperatures[:5])

    print("Total timestamps:", len(timestamps))
    print("Total temperatures:", len(temperatures))

    # TASK 10: Convert API response into a pandas DataFrame
    df = pd.DataFrame({
        "recorded_at": timestamps,
        "temperature_c": temperatures
    })

    print("\nFirst 5 rows of the DataFrame:")
    print(df.head())

    # TASK 11: Inspect DataFrame columns
    print("\nColumn names:")
    print(df.columns)

    print("\nData types before conversion:")
    print(df.dtypes)

    # Convert timestamps into datetime objects
    df["recorded_at"] = pd.to_datetime(df["recorded_at"])

    print("\nData types after conversion:")
    print(df.dtypes)

    print("\nDataFrame information:")
    df.info()

    print("\nFirst 5 rows after conversion:")
    print(df.head())

    # TASK 12: Check for missing values
    print("\nMissing values per column:")
    print(df.isnull().sum())

    # Check for duplicate timestamps
    duplicate_count = df.duplicated(
        subset=["recorded_at"]
    ).sum()

    print("\nDuplicate timestamps:", duplicate_count)

    print("\nTotal rows:", len(df))
    print("Unique timestamps:", df["recorded_at"].nunique())

    print("\nData validation summary:")

    if df.isnull().sum().sum() == 0:
        print("No missing values found.")
    else:
        print("Warning: Missing values detected.")

    if duplicate_count == 0:
        print("No duplicate timestamps found.")
    else:
        print("Warning: Duplicate timestamps detected.")

    # TASK 13: Compare API data with original 2025 CSV

    # Locate project root and original cleaned CSV
    project_root = Path(__file__).resolve().parent.parent

    original_path = (
        project_root / "data" / "hamilton_weather_2025_clean.csv"
    )

    print("\nOriginal CSV path:", original_path)

    if not original_path.exists():
        print("Original cleaned CSV not found.")
        print("Check the filename in your data folder.")

    else:
        # Load original dataset
        original_df = pd.read_csv(original_path)

        # Rename original CSV columns to match API DataFrame
        original_df = original_df.rename(columns={
            "time": "recorded_at",
            "temperature_2m (°C)": "temperature_c"
        })

        print("\nOriginal CSV columns:")
        print(original_df.columns.tolist())

        # Standardize timestamp data types
        original_df["recorded_at"] = pd.to_datetime(
            original_df["recorded_at"]
        )

        # Ensure temperatures are numeric
        original_df["temperature_c"] = pd.to_numeric(
            original_df["temperature_c"],
            errors="coerce"
        )

        # Compare row counts
        print("\nOriginal CSV rows:", len(original_df))
        print("New API rows:", len(df))

        # Compare date ranges
        print("\nOriginal date range:")
        print(original_df["recorded_at"].min())
        print(original_df["recorded_at"].max())

        print("\nAPI date range:")
        print(df["recorded_at"].min())
        print(df["recorded_at"].max())

        # Compare records by timestamp
        comparison = original_df.merge(
            df,
            on="recorded_at",
            how="outer",
            suffixes=("_original", "_api"),
            indicator=True,
            validate="one_to_one"
        )

        print("\nTimestamp matching:")
        print(comparison["_merge"].value_counts())

        # Select timestamps found in both datasets
        matched = comparison[
            comparison["_merge"] == "both"
        ].copy()

        # Calculate absolute temperature differences
        matched["temperature_difference"] = (
            matched["temperature_c_original"]
            - matched["temperature_c_api"]
        ).abs()

        # Count readings that differ by more than 0.01°C
        different_readings = (
            matched["temperature_difference"] > 0.01
        ).sum()

        print("\nReadings with temperature differences > 0.01°C:")
        print(different_readings)

        print("\nMaximum temperature difference:")
        print(matched["temperature_difference"].max())

        print("\nFirst 5 matching records:")
        print(matched.head())

        # Final comparison summary
        print("\nTASK 13 COMPARISON SUMMARY")

        timestamp_match = (
            len(comparison) == len(df) == len(original_df)
            and (comparison["_merge"] == "both").all()
        )

        temperature_match = (
            len(matched) == len(df)
            and matched["temperature_difference"].notna().all()
            and (matched["temperature_difference"] <= 0.01).all()
        )

        if timestamp_match and temperature_match:
            print("SUCCESS: Both datasets match within 0.01°C.")
        else:
            print("WARNING: Differences detected between datasets.")
            print("Review the comparison results before proceeding.")

    # TASK 14: Save processed API data to a separate CSV

    output_path = (
        project_root / "data" / "hamilton_weather_2025_api_processed.csv"
    )

    # Prevent accidental overwriting
    if output_path.exists():
        print("\nProcessed API CSV already exists.")
        print("File was not overwritten.")

    else:
        # Save the processed DataFrame
        df.to_csv(output_path, index=False)

        print("\nProcessed API CSV saved successfully!")
        print("Saved to:", output_path)

    # Verify the saved CSV
    saved_df = pd.read_csv(output_path)

    print("\nSaved CSV row count:", len(saved_df))
    print("Saved CSV columns:", saved_df.columns.tolist())

    if len(saved_df) == 8760:
        print("SUCCESS: Processed CSV contains 8760 rows.")
    else:
        print("WARNING: Unexpected number of rows.")

except requests.exceptions.RequestException as error:
    print("API request failed:", error)

except (KeyError, TypeError, ValueError) as error:
    print("Error processing data:", error)

except pd.errors.ParserError as error:
    print("Error reading CSV:", error)

except OSError as error:
    print("File operation failed:", error)
