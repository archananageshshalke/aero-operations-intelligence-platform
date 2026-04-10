import pandas as pd
import numpy as np
import os

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

# ================================
# LOAD RAW DATA
# ================================
df = pd.read_csv("data/raw/flights.csv")

print("✅ Raw Data Loaded:", len(df))

# ================================
# REMOVE CANCELLED FLIGHTS
# ================================
df = df[df["CANCELLED"] == 0].copy()

print("✅ After Removing Cancelled:", len(df))

# ================================
# TIME CLEANING
# ================================
def format_time(x):
    if pd.isna(x):
        return np.nan
    return str(int(x)).zfill(4)

time_cols = [
    "SCHEDULED_DEPARTURE",
    "DEPARTURE_TIME",
    "SCHEDULED_ARRIVAL",
    "ARRIVAL_TIME"
]

for col in time_cols:
    df[col] = df[col].apply(format_time)

# ================================
# CREATE DATE COLUMN
# ================================
df["FLIGHT_DATE"] = pd.to_datetime(
    df["YEAR"].astype(str) + "-" +
    df["MONTH"].astype(str) + "-" +
    df["DAY"].astype(str),
    errors='coerce'
)

# ================================
# CREATE FEATURES
# ================================
df["IS_DELAYED"] = df["DEPARTURE_DELAY"].apply(lambda x: 1 if x > 15 else 0)

# ================================
# SAVE CLEAN DATA
# ================================
os.makedirs("data/processed", exist_ok=True)

df.to_csv("data/processed/flights_cleaned.csv", index=False)

print("✅ Cleaned data saved")