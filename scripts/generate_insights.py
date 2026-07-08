from sqlalchemy import create_engine, text

# Connect to the SQLite database
engine = create_engine("sqlite:///database/sales.db")

# Run a SQL query
query = """
SELECT
    Region,
    ROUND(SUM(Sales), 2) AS Total_Sales,
    ROUND(SUM(Profit), 2) AS Total_Profit
FROM sales
GROUP BY Region
ORDER BY Total_Sales DESC;
"""

# Display the results
with engine.connect() as connection:
    results = connection.execute(text(query))

    print("Sales and Profit by Region")
    print("-" * 55)

    for row in results:
        print(
            f"{row.Region:<10} | "
            f"Sales: ${row.Total_Sales:>12,.2f} | "
            f"Profit: ${row.Total_Profit:>10,.2f}"
        )