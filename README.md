# Polars 2.0 Benchmark Lab

A small, reproducible benchmark lab for exploring the upcoming **Polars 2.0** release.

The repository accompanies my Polars 2.0 experiments and benchmarks. It focuses primarily on the changes around the execution engine and compares:

- Polars 1.44
- Polars 2.0
- the default `auto` engine
- the `in-memory` engine

The main benchmark uses up to **100 million rows** and measures both execution time and peak memory usage.

> **Important:** The current results were produced with a Polars 2.0 release candidate. They are an early look at Polars 2.0, not final-release benchmarks. The benchmarks will be rerun once Polars 2.0 is officially released.

## Requirements

You need:

- Linux
- Git
- Python
- [uv](https://docs.astral.sh/uv/)

The benchmark scripts use `/usr/bin/time -v` for independent peak-memory measurements, so Linux is currently the recommended environment.

You do **not** need to install Polars manually. `uv` creates the required environments and installs the appropriate Polars versions.

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

## Install uv

If `uv` is not installed yet, follow the official installation instructions:

https://docs.astral.sh/uv/getting-started/installation/

Verify the installation:

```bash
uv --version
```

## Install the Project

From the repository directory:

```bash
uv sync
```

This creates the local virtual environment and installs the project dependencies defined in `pyproject.toml`.

## Benchmark Data

The generated benchmark datasets are intentionally **not stored in Git**.

The full benchmark creates large local Parquet files, including datasets containing up to 100 million rows.

They are excluded through `.gitignore`:

```text
data/*.parquet
```

This keeps the repository small and makes the experiment reproducible: every user generates the same synthetic benchmark data locally.

## Run the Benchmarks

The complete benchmark suite can be started with:

```bash
bash run_benchmarks.sh
```

The script creates the required benchmark data and runs the different Polars configurations.

Depending on the machine, the full benchmark may take some time and requires several gigabytes of available RAM.

For the 100-million-row tests, make sure your system has sufficient free memory before starting the benchmark.

## What Is Being Compared?

The benchmark focuses on two workloads.

### Lazy Pipeline

A synthetic dataset containing up to 100 million rows is processed using a lazy Polars query containing operations such as:

```text
scan_parquet
→ filter
→ expressions
→ group_by
→ aggregations
→ sort
```

The benchmark compares execution time and peak memory consumption across Polars versions and execution engines.

### Join Pipeline

A second workload joins a large transaction dataset with customer data before filtering and aggregating the result:

```text
transactions
→ join customers
→ filter
→ group_by
→ aggregations
→ sort
```

This provides a more demanding test of the Polars execution engine.

## Memory Measurement

The Python benchmark scripts report their own runtime and peak RSS.

The benchmark runner additionally uses:

```bash
/usr/bin/time -v
```

The important external measurement is:

```text
Maximum resident set size
```

This gives us an independent measurement of the maximum physical memory used by the process.

The benchmarks are repeated several times so that individual runs do not determine the final result.

For comparisons, the **median runtime and median peak RSS** should be used.

## Reproducing the Experiment

For the most comparable results:

1. Close memory-intensive applications.
2. Generate the benchmark datasets locally.
3. Run the complete benchmark suite.
4. Let every configuration run all repetitions.
5. Compare medians rather than individual runs.

The benchmark is primarily designed to compare **execution-engine behavior**, not storage or disk performance.

Because the same Parquet files are read repeatedly, operating-system filesystem caching can affect I/O. This is intentional: the experiment focuses on query execution and memory behavior rather than cold-disk throughput.

## Synthetic Data

The benchmark data is synthetic and deliberately simple.

Because many values repeat, Parquet can compress the datasets extremely well. A file containing 100 million rows can therefore be much smaller on disk than its row count might suggest.

The benchmark should consequently **not** be interpreted as a comparison of Parquet compression ratios or disk I/O performance.

Its purpose is to compare how the different Polars execution strategies process the same workload.

## Migration Experiments

The repository also contains smaller experiments for investigating behavioral and API changes in Polars 2.0.

These include areas such as:

- execution-engine behavior
- join row ordering
- SQL behavior
- deprecated and removed APIs
- `cut` / `qcut` changes
- Parquet behavior

Some of these experiments currently target the Polars 2.0 release candidate and will be rerun against the final release.

## Repository Structure

```text
polars-2-lab/
├── benchmark.sh
├── main.py
├── pyproject.toml
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
│   └── generated locally
└── results/
    └── benchmark results
```

## A Note About Polars 2.0

This repository currently tracks the **Polars 2.0 release candidate**.

That distinction matters.

Release-candidate behavior, performance, warnings, and APIs may still change before the final release. Results in this repository should therefore be treated as reproducible observations of the tested RC rather than definitive Polars 2.0 performance claims.

Once the stable Polars 2.0 release is available, the benchmark suite will be rerun without changing the workloads.

That will allow a direct comparison between the release candidate and the final release.

## Related Article

This repository contains the complete experiments behind my upcoming Polars 2.0 articles on Medium.

The first article takes an early look at the surprisingly large memory difference observed with the new execution behavior.

The full Polars 2.0 review will follow after the final release, including updated benchmarks and the migration changes that matter in practice.
