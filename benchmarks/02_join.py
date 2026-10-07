import argparse
import json
import resource
import sys
import time
from pathlib import Path

import polars as pl

DATA_DIR = Path("data")
LEFT = DATA_DIR / "transactions.parquet"
RIGHT = DATA_DIR / "customers.parquet"


def create_data(rows: int) -> None:
    DATA_DIR.mkdir(exist_ok=True)

    customer_rows = max(rows // 20, 100_000)

    if not RIGHT.exists():
        print(f"Creating {customer_rows:,} customers...")

        customers = pl.DataFrame(
            {
                "customer_id": pl.arange(0, customer_rows, eager=True),
                "segment": pl.arange(0, customer_rows, eager=True) % 20,
                "country": pl.arange(0, customer_rows, eager=True) % 50,
            }
        )

        customers.write_parquet(RIGHT, compression="zstd")

    if not LEFT.exists():
        print(f"Creating {rows:,} transactions...")

        chunk_size = 1_000_000
        parts = []

        for start in range(0, rows, chunk_size):
            n = min(chunk_size, rows - start)

            ids = pl.arange(start, start + n, eager=True)

            part = pl.DataFrame(
                {
                    "transaction_id": ids,
                    "customer_id": ids % customer_rows,
                    "amount": ((ids % 10_000) / 100).cast(pl.Float64),
                }
            )

            parts.append(part)

        pl.concat(parts).write_parquet(
            LEFT,
            compression="zstd",
        )

    print(f"{LEFT}: {LEFT.stat().st_size / 1024**2:.1f} MB")
    print(f"{RIGHT}: {RIGHT.stat().st_size / 1024**2:.1f} MB")


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

    if not LEFT.exists() or not RIGHT.exists():
        raise SystemExit("Datasets missing. Run with --create first.")

    print(f"Polars: {pl.__version__}")
    print(f"Engine: {args.engine}")

    transactions = pl.scan_parquet(LEFT)
    customers = pl.scan_parquet(RIGHT)

    query = (
        transactions.join(
            customers,
            on="customer_id",
            how="inner",
        )
        .filter(pl.col("amount") > 25)
        .group_by(["segment", "country"])
        .agg(
            pl.len().alias("transactions"),
            pl.col("amount").sum().alias("revenue"),
            pl.col("amount").mean().alias("avg_transaction"),
        )
        .sort(["segment", "country"])
    )

    start = time.perf_counter()

    result = query.collect(engine=args.engine)

    elapsed = time.perf_counter() - start
    peak_mb = peak_memory_mb()

    checksum = float(result["revenue"].sum())

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
