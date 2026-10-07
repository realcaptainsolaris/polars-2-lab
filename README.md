## Polars 2.0 Migration Lab

Baseline: Polars 1.44.2
Candidate: Polars 2.0.0-rc.2

### Current findings

#### Default streaming engine

No observable result difference in the initial minimal join test.

#### SQL semantics

The SQL changes documented in the Polars 2.0 upgrade guide are not
observable in 2.0.0-rc.2.

Tested:

- decimal numeric literals
- modulo with negative operands
- DIV with negative operands
- ROUND tie-breaking

RC2 currently behaves identically to Polars 1.44.2 in these tests.

These tests must be repeated against the final Polars 2.0.0 release.
