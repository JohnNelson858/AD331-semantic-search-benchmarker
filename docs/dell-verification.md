# Dell verification

Reported by John Nelson on November 10, 2026, with supplied screenshots.

- Live exact-identifier and conceptual comparator examples worked.
- At K=5: Dense 256 Hit Rate/Recall 0.500, MRR 0.370; dense 1024 Hit Rate/Recall 0.722, MRR 0.562; dense structural Hit Rate/Recall 0.722, MRR 0.602; BM25 structural Hit Rate/Recall 0.611, MRR 0.528.
- Mean search lookup ms: 2.419 / 2.090 / 1.879 / 1.689 in the same row order. Dense query encoding mean: 16.822 ms, reported separately from lookup.
- Tests: 16 passed, 1 warning in 74.97 seconds. Warning: Starlette test-client httpx deprecation.
- Original Docker build completed successfully; `docker compose ps` showed healthy on port 8002. Docker Desktop showed the container running. Reported idle container memory was 3.199 GiB, motivating the subsequent optimization.
- The optimized Docker rebuild, cloud deployment, actual video runtime and final submission remain unverified.
