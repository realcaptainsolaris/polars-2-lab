# Polars 2.0 Benchmark Lab

Reproducible benchmarks and migration experiments for **Polars 2.0.0**.

The main benchmark processes **100 million rows** and compares the default `auto` execution engine with the `in-memory` engine.

The result on my test machine:

| Benchmark | Engine | Median Runtime | Median Peak RAM |
|---|---|---:|---:|
| 100M pipeline | Polars 2.0 `auto` | **0.414 s** | **592 MB** |
| 100M pipeline | Polars 2.0 `in-memory` | 1.061 s | 4.56 GB |
| 100M join | Polars 2.0 `auto` | **1.297 s** | **691 MB** |
| 100M join | Polars 2.0 `in-memory` | 1.729 s | 4.76 GB |

For the main pipeline, `auto` used roughly **87% less peak memory** while running about **2.6× faster**.

The repository contains everything needed to reproduce the tests locally.

## Why This Repository Exists

Polars 2.0 changes the default execution behavior of lazy queries.

With Polars 2.0, `engine="auto"` can use the streaming engine instead of the traditional in-memory execution path.

For large datasets, that can dramatically change memory consumption.

This repository provides reproducible experiments for investigating that behavior instead of relying on small synthetic timing snippets.

It also contains migration experiments for selected Polars 2.0 API and behavioral changes.

## Requirements

The benchmarks are designed primarily for Linux.

You need:

- Git
- Python
- [uv](https://docs.astral.sh/uv/)
- `/usr/bin/time`

The benchmark scripts use `/usr/bin/time -v` to independently measure maximum resident set size.

## Clone the Repository

Using SSH:

```bash
git clone git@github.com:realcaptainsolaris/polars-2-lab.git
cd polars-2-lab
```

Or using HTTPS:

```bash
git clone https://github.com/realcaptainsolaris/polars-2-lab.git
cd polars-2-lab
```

## Install the Environment

Dependencies are managed with `uv`.

```bash
uv sync
```

No benchmark datasets are stored in Git.

They are generated locally when needed.

## Run the Benchmarks

Run the complete benchmark suite with:

```bash
bash run_benchmarks.sh
```

The script runs the benchmark configurations repeatedly so that results can be compared using medians instead of relying on a single execution.

The suite compares:

- Polars 1.44.2 with `engine="auto"`
- Polars 2.0.0 with `engine="auto"`
- Polars 2.0.0 with `engine="in-memory"`

It runs both the main aggregation pipeline and the join workload.

## Benchmark 1: 100 Million Row Pipeline

The first benchmark creates a synthetic Parquet dataset containing **100 million rows**.

The lazy query performs:

```text
scan_parquet
    ↓
filter
    ↓
expressions
    ↓
group_by
    ↓
aggregations
    ↓
sort
```

The same query is executed using different Polars versions and execution engines.

The important Polars 2.0 comparison is:

```python
result = query.collect(engine="auto")
```

versus:

```python
result = query.collect(engine="in-memory")
```

No query logic changes between those runs.

### Results

Median of five runs:

| Engine | Runtime | Peak RAM |
|---|---:|---:|
| Polars 2.0 `auto` | **0.414 s** | **592 MB** |
| Polars 2.0 `in-memory` | 1.061 s | 4.56 GB |

In this workload, automatic execution required approximately **87% less peak memory**.

It was also approximately **2.6× faster**.

## Benchmark 2: 100 Million Row Join

The second workload uses:

- 100 million transactions
- 1 million customers
- an inner join
- filtering
- grouping
- multiple aggregations
- sorting

Again, the query itself remains unchanged between execution engines.

### Results

Median of five runs:

| Engine | Runtime | Peak RAM |
|---|---:|---:|
| Polars 2.0 `auto` | **1.297 s** | **691 MB** |
| Polars 2.0 `in-memory` | 1.729 s | 4.76 GB |

Here, `auto` reduced peak memory by roughly **85%** while also reducing runtime by approximately **25%**.

## Comparing Polars 1.44 and 2.0

The suite also runs Polars 1.44.2.

This is useful because `engine="auto"` does not imply identical execution behavior across the two major versions.

For example, the join benchmark produced a median runtime of roughly:

```text
Polars 1.44.2 auto
~1.99 s
~4.71 GB peak RAM
```

compared with:

```text
Polars 2.0.0 auto
~1.30 s
~691 MB peak RAM
```

The goal is not to claim that every Polars workload will see improvements of this magnitude.

The benchmark demonstrates how significantly the execution behavior can change for workloads that benefit from streaming.

## Dataset Generation

The datasets are intentionally **not committed to Git**.

They are generated locally.

This keeps the repository small and makes the experiment reproducible without distributing hundreds of megabytes of generated benchmark data.

The main 100-million-row Parquet file is highly compressible because the synthetic values repeat frequently.

As a result, the file is only approximately:

```text
116 MB
```

on disk.

This is important when interpreting the results.

The benchmark is not intended to demonstrate Parquet compression or raw disk throughput.

## Benchmark Methodology

Each important configuration is executed **five times**.

The reported numbers use the median.

Runtime is measured around query execution.

Peak process memory is additionally measured using:

```bash
/usr/bin/time -v
```

and its:

```text
Maximum resident set size
```

measurement.

The benchmark is deliberately focused on:

- query execution
- execution-engine behavior
- peak memory consumption

It is **not a cold disk-I/O benchmark**.

Repeated runs benefit from the operating system filesystem cache.

That is intentional for this experiment.

## Important Caveats

These are synthetic benchmarks.

Real-world performance depends on factors including:

- data distribution
- column types
- query structure
- join cardinality
- available memory
- CPU
- storage
- operating system
- Polars query optimization

Do not interpret the numbers in this repository as universal Polars performance numbers.

The useful comparison is the behavior of different execution strategies under the **same workload on the same machine**.

## Migration Experiments

The repository also contains small experiments related to Polars 2.0 migration behavior.

```text
migration/
├── 01_engine_default.py
├── 02_sql_literals.py
├── 03_parquet_enum.py
├── 04_cut_qcut.py
└── 05_migration_gotchas.py
```

These experiments investigate areas such as:

- execution-engine changes
- SQL behavior
- Parquet type handling
- deprecated APIs
- removed APIs
- ordering behavior

One particularly important migration detail is that streaming execution can produce different row ordering for operations such as joins.

If downstream code depends on row order, make that requirement explicit rather than relying on incidental execution order.

## Repository Structure

```text
polars-2-lab/
├── run_benchmarks.sh
├── main.py
├── pyproject.toml
├── README.md
├── migration/
│   ├── 01_engine_default.py
│   ├── 02_sql_literals.py
│   ├── 03_parquet_enum.py
│   ├── 04_cut_qcut.py
│   └── 05_migration_gotchas.py
├── benchmarks/
│   ├── 01_streaming_memory.py
│   └── 02_join.py
├── data/
└── results/
```

## Official Polars 2.0 Resources

- [Polars 2.0 — Official Release Announcement](https://pola.rs/posts/release-polars-2/)
- [Polars 2.0 — Official Upgrade Guide](https://docs.pola.rs/releases/upgrade/2/)
- [Polars 2.0.0 on PyPI](https://pypi.org/project/polars/2.0.0/)

## Reproduce the Results

The shortest path from clone to benchmark is:

```bash
git clone git@github.com:realcaptainsolaris/polars-2-lab.git
cd polars-2-lab
uv sync
bash run_benchmarks.sh
```

Then compare your results with the numbers above.

Different hardware will produce different runtimes.

The interesting question is whether you see the same dramatic difference in **peak memory consumption** between the execution engines.

If you do, I'd be interested to hear what numbers you get.
