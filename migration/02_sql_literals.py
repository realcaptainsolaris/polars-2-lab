import polars as pl

print(f"Polars: {pl.__version__}")

queries = [
    "SELECT 1.5 AS value",
    "SELECT 1.5e0 AS value",
    "SELECT -7 % 2 AS value",
    "SELECT DIV(-7.5, 2) AS value",
    "SELECT ROUND(2.5) AS value",
]

for sql in queries:
    print(f"\n{sql}")

    result = pl.SQLContext().execute(sql).collect()

    print(result)
    print("dtype:", result.schema["value"])
