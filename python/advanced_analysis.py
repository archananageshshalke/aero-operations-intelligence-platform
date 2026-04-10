import pandas as pd
import numpy as np

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

# ================================
# LOAD CLEANED DATA
# ================================
df = pd.read_csv("data/processed/flights_cleaned.csv")

print("✅ Data Loaded:", len(df))

# ================================
# PREPARE TIME
# ================================
df["DEPARTURE_TIME"] = pd.to_numeric(df["DEPARTURE_TIME"], errors='coerce')

df["FULL_DATETIME"] = pd.to_datetime(
    df["FLIGHT_DATE"].astype(str) + " " +
    df["DEPARTURE_TIME"].fillna(0).astype(int).astype(str).str.zfill(4),
    format="%Y-%m-%d %H%M",
    errors='coerce'
)

df = df.sort_values(by=["TAIL_NUMBER", "FULL_DATETIME"])

# ================================
# DELAY PROPAGATION
# ================================
df["PREV_DELAY"] = df.groupby("TAIL_NUMBER")["DEPARTURE_DELAY"].shift(1)

df["DELAY_PROPAGATION"] = np.where(
    (df["PREV_DELAY"] > 15) & (df["DEPARTURE_DELAY"] > 15),
    1, 0
)

# ================================
# AIRCRAFT ANALYSIS
# ================================
aircraft_stats = df.groupby("TAIL_NUMBER").agg(
    AVG_DELAY=("DEPARTURE_DELAY", "mean"),
    PROPAGATION_COUNT=("DELAY_PROPAGATION", "sum"),
    TOTAL_FLIGHTS=("FLIGHT_NUMBER", "count")
).sort_values(by="PROPAGATION_COUNT", ascending=False)

print("\n🔥 Top Aircraft:")
print(aircraft_stats.head(10))

# ================================
# ROUTE ANALYSIS
# ================================
route_stats = df.groupby(["ORIGIN_AIRPORT", "DESTINATION_AIRPORT"]).agg(
    AVG_DELAY=("DEPARTURE_DELAY", "mean"),
    PROPAGATION=("DELAY_PROPAGATION", "sum"),
    FLIGHTS=("FLIGHT_NUMBER", "count")
)

route_stats = route_stats[route_stats["FLIGHTS"] > 100]
route_stats = route_stats.sort_values(by="AVG_DELAY", ascending=False)

print("\n🔥 Worst Routes:")
print(route_stats.head(10))

# ================================
# TIME ANALYSIS
# ================================
df["DEP_HOUR"] = df["DEPARTURE_TIME"] // 100

time_stats = df.groupby("DEP_HOUR")["DEPARTURE_DELAY"].mean()

print("\n🔥 Delay by Hour:")
print(time_stats)

# ================================
# BUFFER RISK
# ================================
df["NEXT_DEP_TIME"] = df.groupby("TAIL_NUMBER")["FULL_DATETIME"].shift(-1)

df["TURNAROUND_MIN"] = (df["NEXT_DEP_TIME"] - df["FULL_DATETIME"]).dt.total_seconds() / 60

df["BUFFER_RISK"] = np.where(
    (df["TURNAROUND_MIN"] < 40) & (df["DEPARTURE_DELAY"] > 15),
    1, 0
)

print("\n🔥 Buffer Risk Flights:", int(df["BUFFER_RISK"].sum()))

# ================================
# SAVE OUTPUTS
# ================================
aircraft_stats.to_csv("data/processed/aircraft_analysis.csv")
route_stats.to_csv("data/processed/route_analysis.csv")

print("\n✅ Analysis complete")