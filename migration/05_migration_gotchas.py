import warnings

import polars as pl

warnings.simplefilter("always")

print("=" * 70)
print(f"Polars {pl.__version__}")
print("=" * 70)

print("\n1. CUT / QCUT")

df = pl.DataFrame(
    {
        "value": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0],
    }
)

try:
    print(df.with_columns(pl.col("value").cut([2.0, 4.0]).alias("bin")))
except Exception as exc:
    print(type(exc).__name__, exc)

print("\n2. NEW BIN API")

for method in [
    "bin_intervals",
    "bin_quantiles",
    "bin_ranks",
]:
    print(
        method,
        "available:",
        hasattr(pl.col("value"), method),
    )

print("\n3. SQL SEMANTICS")

queries = [
    "SELECT 1.5 AS value",
    "SELECT 1.5e0 AS value",
    "SELECT -7 % 2 AS value",
    "SELECT DIV(-7.5, 2) AS value",
    "SELECT ROUND(2.5) AS value",
]

for sql in queries:
    try:
        result = pl.SQLContext().execute(sql).collect()

        print(
            sql,
            "=>",
            result.item(),
            "/",
            result.schema["value"],
        )

    except Exception as exc:
        print(
            sql,
            "=>",
            type(exc).__name__,
            exc,
        )

print("\n4. REMOVED / DEPRECATED APIs")

checks = [
    ("DataFrame.melt", pl.DataFrame, "melt"),
    ("DataFrame.with_row_count", pl.DataFrame, "with_row_count"),
    ("LazyFrame.fetch", pl.LazyFrame, "fetch"),
    ("LazyFrame.profile", pl.LazyFrame, "profile"),
]

for label, obj, attribute in checks:
    print(
        f"{label}:",
        "available" if hasattr(obj, attribute) else "REMOVED",
    )

print("\n5. ENGINE / JOIN ORDER")

left = pl.LazyFrame(
    {
        "key": [3, 1, 4, 2, 5],
        "left_value": ["c", "a", "d", "b", "e"],
    }
)

right = pl.LazyFrame(
    {
        "key": [5, 4, 3, 2, 1],
        "right_value": ["E", "D", "C", "B", "A"],
    }
)

query = left.join(
    right,
    on="key",
    how="inner",
)

try:
    auto = query.collect(engine="auto")
    print("\nauto:")
    print(auto)
except Exception as exc:
    print("auto:", type(exc).__name__, exc)

try:
    memory = query.collect(engine="in-memory")
    print("\nin-memory:")
    print(memory)
except Exception as exc:
    print("in-memory:", type(exc).__name__, exc)

print("\n6. VERSION")

print(pl.show_versions())
