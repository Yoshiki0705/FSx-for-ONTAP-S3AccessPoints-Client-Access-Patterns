# Benchmarks

🌐 **Language**: [日本語](README.md) | **English**

> **Real runs need approval**: Measuring on real infrastructure can cost money, so run it by hand only after you have shown the cost estimate and the cleanup steps and the user has approved. CI never runs it.

## Policy

- Only records with every environment field of [docs/templates/benchmark-record.en.md](../docs/templates/benchmark-record.en.md) filled in go under `records/`.
- Every measured value states whether it is a sample run or a production estimate. The default is a sample run.
- Evidence that disappears at teardown (bucket contents, files on a throwaway volume) is copied to `records/` before teardown.

## Scripts

`scripts/run_benchmark.py` is a dry run that connects to nothing by default. Run it with `make bench-dry-run`. Connecting to real infrastructure is not implemented in this repository's scripts yet.
