import sys

import polars as pl
import pyarrow as pa
import pyarrow.parquet as pq

PATH = "/tmp/polars_enum_test.parquet"


def create_parquet():
    values = pa.array(
        ["pending", "running", "finished", "running"],
        type=pa.dictionary(
            pa.int32(),
            pa.string(),
        ),
    )

    table = pa.table({"status": values})

    pq.write_table(
        table,
        PATH,
    )


create_parquet()

print(f"Python: {sys.version.split()[0]}")
print(f"Polars: {pl.__version__}")

df = pl.read_parquet(PATH)

print("\nDataFrame:")
print(df)

print("\nSchema:")
print(df.schema)

print("\nstatus dtype:")
print(df.schema["status"])


parquet_file = pq.ParquetFile(PATH)

print("\nParquet schema:")
print(parquet_file.schema)

print("\nArrow schema:")
print(parquet_file.schema_arrow)
