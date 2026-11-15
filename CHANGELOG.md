# 0.1.1 — 2026-11-15

- Corrupted DEFLATE data now produces integrity_error JSON and exit 2 instead of an uncaught traceback.
- Control characters in archive paths are rejected.
- Windows-forbidden filename characters are reported.
- Fourteen regression tests pass; no telemetry or dependencies added.
