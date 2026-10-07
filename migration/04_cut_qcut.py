import warnings

import polars as pl

warnings.simplefilter("always")

print(f"Polars: {pl.__version__}")

df = pl.DataFrame(
    {
        "value": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0],
    }
)

print("\n--- cut() ---")

result = df.with_columns(pl.col("value").cut([2.0, 4.0]).alias("bin"))

print(result)
print("dtype:", result.schema["bin"])

print("\n--- qcut() ---")

result = df.with_columns(pl.col("value").qcut([0.5]).alias("bin"))

print(result)
print("dtype:", result.schema["bin"])


print("\n--- bin_intervals() default ---")

result = df.with_columns(pl.col("value").bin_intervals([2.0, 4.0]).alias("bin"))

print(result)
print("dtype:", result.schema["bin"])

print("\n--- bin_intervals(right_closed=True) ---")

result = df.with_columns(
    pl.col("value")
    .bin_intervals(
        [2.0, 4.0],
        right_closed=True,
    )
    .alias("bin")
)

print(result)
print("dtype:", result.schema["bin"])
