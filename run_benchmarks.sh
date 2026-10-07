#!/usr/bin/env bash

set -e

for i in {1..5}; do
  echo "===== RUN $i / PIPELINE / POLARS 1.44 AUTO ====="
  /usr/bin/time -v uv run --with polars==1.44.2 \
    benchmarks/01_streaming_memory.py --engine auto

  echo "===== RUN $i / PIPELINE / POLARS 2.0 AUTO ====="
  /usr/bin/time -v uv run --with polars==2.0.0rc2 \
    benchmarks/01_streaming_memory.py --engine auto

  echo "===== RUN $i / PIPELINE / POLARS 2.0 IN-MEMORY ====="
  /usr/bin/time -v uv run --with polars==2.0.0rc2 \
    benchmarks/01_streaming_memory.py --engine in-memory

  echo "===== RUN $i / JOIN / POLARS 1.44 AUTO ====="
  /usr/bin/time -v uv run --with polars==1.44.2 \
    benchmarks/02_join.py --engine auto

  echo "===== RUN $i / JOIN / POLARS 2.0 AUTO ====="
  /usr/bin/time -v uv run --with polars==2.0.0rc2 \
    benchmarks/02_join.py --engine auto

  echo "===== RUN $i / JOIN / POLARS 2.0 IN-MEMORY ====="
  /usr/bin/time -v uv run --with polars==2.0.0rc2 \
    benchmarks/02_join.py --engine in-memory
done
