import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, text

# File paths
CLEAN_FILE = Path("data/processed/superstore_clean.csv")
DATABASE_FILE = Path("database/sales.db")

# Make sure the database folder exists
DATABASE_FILE.parent.mkdir(parents=True, exist_ok=True)

# Read cleaned data
df = pd.read_csv(CLEAN_FILE)

# Create connection to SQLite database
engine = create_engine(f"sqlite:///{DATABASE_FILE}")

# Load data into a table called sales
df.to_sql("sales", engine, if_exists="replace", index=False)

# Verify the data was loaded successfully
with engine.connect() as connection:
    row_count = connection.execute(text("SELECT COUNT(*) FROM sales")).scalar()

print("Database created successfully.")
print(f"Rows loaded into sales table: {row_count}")
print(f"Database saved to: {DATABASE_FILE}")