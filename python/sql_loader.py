import pandas as pd
import sqlite3

# Load cleaned data
df = pd.read_csv("data/processed/flights_cleaned.csv")

# Create database
conn = sqlite3.connect("airline.db")

# Load into SQL
df.to_sql("flights", conn, if_exists="replace", index=False)

print("✅ SQL loaded successfully")