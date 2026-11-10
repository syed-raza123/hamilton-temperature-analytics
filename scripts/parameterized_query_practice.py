import pandas as pd

df = pd.read_csv(
    "data/hamilton_weather_2025_api_processed.csv",
    parse_dates=["recorded_at"]
)

print(df.columns.tolist())
print(df.dtypes)