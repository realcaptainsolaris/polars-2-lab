import polars as pl

print(f"Polars: {pl.__version__}")

left = pl.LazyFrame(
    {
        "k": [0, 1, 2],
        "left_value": ["a", "b", "c"],
    }
)

right = pl.LazyFrame(
    {
        "k": [2, 1, 0],
        "right_value": ["x", "y", "z"],
    }
)

query = left.join(
    right,
    on="k",
    how="left",
)

print("\nengine=auto")
print(query.collect())

print("\nengine=in-memory")
print(query.collect(engine="in-memory"))

print("\nExplicitly preserving left order")
print(
    left.join(
        right,
        on="k",
        how="left",
        maintain_order="left",
    ).collect()
)
