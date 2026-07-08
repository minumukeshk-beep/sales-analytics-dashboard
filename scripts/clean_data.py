import pandas as pd
from pathlib import Path

# Project folders
RAW_FILE = Path("data/raw/superstore_raw.csv")
PROCESSED_FILE = Path("data/processed/superstore_clean.csv")

# Read the original CSV file
df = pd.read_csv(RAW_FILE)

# Remove extra spaces from column names
df.columns = df.columns.str.strip()

# Rename columns to Python-friendly names
df = df.rename(columns={
    "Ship Mode": "Ship_Mode",
    "Sub-Category": "Sub_Category",
    "Postal Code": "Postal_Code"
})

# Remove duplicate rows
before_duplicates = len(df)
df = df.drop_duplicates()
duplicates_removed = before_duplicates - len(df)

# Clean text columns
text_columns = [
    "Ship_Mode", "Segment", "Country", "City", "State",
    "Region", "Category", "Sub_Category"
]

for column in text_columns:
    if column in df.columns:
        df[column] = df[column].astype(str).str.strip()

# Convert numeric columns safely
numeric_columns = ["Postal_Code", "Sales", "Quantity", "Discount", "Profit"]

for column in numeric_columns:
    if column in df.columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

# Remove rows where important business values are missing
before_nulls = len(df)
df = df.dropna(subset=["Sales", "Quantity", "Discount", "Profit"])
null_rows_removed = before_nulls - len(df)

# Create useful helper columns for dashboard analysis
df["Profit_Margin_Percent"] = (df["Profit"] / df["Sales"] * 100).round(2)
df["Discount_Percent"] = (df["Discount"] * 100).round(2)

# Save the cleaned dataset
PROCESSED_FILE.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(PROCESSED_FILE, index=False)

# Print a simple cleaning report
print("Data cleaning completed successfully.")
print(f"Rows after cleaning: {len(df)}")
print(f"Duplicate rows removed: {duplicates_removed}")
print(f"Rows removed because of missing important values: {null_rows_removed}")
print("\nFinal columns:")
print(df.columns.tolist())
print(f"\nCleaned file saved to: {PROCESSED_FILE}")