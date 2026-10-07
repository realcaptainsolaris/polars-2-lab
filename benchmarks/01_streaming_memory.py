import argparse
import json
import resource
import sys
import time
from pathlib import Path

import polars as pl

DATA = Path("data/events.parquet")


def create_data(rows: int) -> None:
    DATA.parent.mkdir(exist_ok=True)
    if DATA.exists():
        return

    print(f"Creating {rows:,} rows...")

    chunk_size = 1_000_000
    parts = []

    for start in range(0, rows, chunk_size):
        n = min(chunk_size, rows - start)

        part = pl.DataFrame(
            {
                "id": pl.arange(start, start + n, eager=True),
                "group": pl.arange(start, start + n, eager=True) % 1000,
                "value": (pl.arange(start, start + n, eager=True) % 10_000).cast(
                    pl.Float64
                ),
            }
        )

        parts.append(part)

    df = pl.concat(parts)

    df.write_parquet(
        DATA,
        compression="zstd",
    )

    print(f"Created {DATA}: {DATA.stat().st_size / 1024**2:.1f} MB")


def peak_memory_mb() -> float:
    usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

    if sys.platform == "darwin":
        return usage / 1024**2

    return usage / 1024


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=20_000_000)
    parser.add_argument("--engine", default="auto")
    parser.add_argument("--create", action="store_true")

    args = parser.parse_args()

    if args.create:
        create_data(args.rows)

    if not DATA.exists():
        raise SystemExit("Dataset missing. Run with --create first.")

    print(f"Polars: {pl.__version__}")
    print(f"Engine: {args.engine}")
    print(f"Dataset: {DATA}")
    print(f"File size: {DATA.stat().st_size / 1024**2:.1f} MB")

    query = (
        pl.scan_parquet(DATA)
        .filter(pl.col("value") > 2500)
        .with_columns(
            (pl.col("value") * 1.19).alias("gross"),
            (pl.col("value") ** 2).alias("value_squared"),
        )
        .group_by("group")
        .agg(
            pl.len().alias("rows"),
            pl.col("gross").sum().alias("gross_sum"),
            pl.col("value_squared").mean().alias("mean_squared"),
        )
        .sort("group")
    )

    start = time.perf_counter()

    result = query.collect(engine=args.engine)

    elapsed = time.perf_counter() - start
    peak_mb = peak_memory_mb()

    checksum = float(result["gross_sum"].sum())

    print(result.head())

    summary = {
        "polars": pl.__version__,
        "engine": args.engine,
        "elapsed_seconds": round(elapsed, 4),
        "peak_memory_mb": round(peak_mb, 2),
        "result_rows": result.height,
        "checksum": checksum,
    }

    print("\nRESULT")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
