# Deployment memory optimization

Measured November 10, 2026. These are assistant-workspace Linux process values,
not measurements on Render. The Dell's original Docker container separately
reported 3.199 GiB idle usage in John's screenshot.

| Configuration | Peak process memory | Memory after indexing and benchmark |
|---|---:|---:|
| Original: batch 8, default ONNX CPU arena, runtime corpus encoding | 3311.5 MiB | 3312.1 MiB (proc RSS) |
| Batch 1, CPU arena disabled, runtime corpus encoding | 1737.5 MiB | 455.2 MiB |
| Same optimized encoder, corpus vectors loaded from build cache | 329.9 MiB | 329.9 MiB |

The first two peak measurements use Linux `resource.ru_maxrss`; proc RSS and
resource counters can differ slightly. The final probe uses the larger of
`/proc/self/status` VmHWM and ru_maxrss. See the raw
[cached profile](memory-cached-profile.json). The processes exercised indexing
and all 18 benchmark queries. The cached probe also exercised all 18 comparator
searches. Timings are observations, not a hosting SLA; native cached index setup
was about 1.1 seconds, excluding imports.

## Changes and tradeoffs

- Encode one document per batch; do not pad eight documents to the longest
  sequence. Keep the full original text, model, tokenizer, and 512 dimensions.
- Disable ONNX's CPU memory arena so large indexing buffers are not retained.
- Serialize shared-model inference across searches and benchmarks. Under
  overlapping requests, encoding waits instead of allocating parallel buffers.
- Compute real corpus embeddings while building the Docker image. Small NumPy
  files are keyed by model identity, pinned model revision, and ordered chunk
  IDs/content. Live queries still run the real model; Chroma performs real vector
  search. This adds a corpus-encoding step to Docker builds.
- Require the image cache at runtime. A missing/stale cache stops startup with
  an explicit rebuild instruction instead of unexpectedly encoding large
  documents on the small hosting instance. Validate cached shape, dtype, finite
  values and unit lengths; load with `allow_pickle=False`.

All 36 quality metrics across K=3/5/10 matched in uncached before/after runs.
The cached run also matched original K=5 quality: MRR 0.370 / 0.562 / 0.602 /
0.528 for dense 256 / dense 1024 / dense structural / BM25. Existing real-model
tests passed in the uncached path (16 tests); the final cache-enabled suite
passed 18 tests, including cache reuse/invalidation and corrupt cache rejection.
The one warning is the existing upstream Starlette/httpx deprecation.
See [QA output](memory-qa.txt). Historical benchmark timings are preserved;
rerun the UI benchmark to obtain new timings for the target machine.

## Target verification still required

Docker is unavailable in the assistant environment. John must rebuild on the
Dell, confirm healthy startup, exercise both example searches and Run Benchmark,
then check container memory. Compose now enforces a 2 GiB memory limit; this is
a local deployment-budget check, not proof of Render's peak usage. Model
encoding still occurs during image builds and may peak around 1.7 GiB in the
measured workspace. Runtime uses only the baked corpus cache and live queries.

```powershell
docker compose up --build -d --wait
docker compose ps
docker stats --no-stream
```

For a separate fresh-process probe, stop the server first so a second model is
not resident alongside it:

```powershell
docker compose stop search
docker compose run --rm --no-deps search .venv/bin/python -m src.memory_probe
docker compose up -d --wait
```

Only choose the Render tier after the updated container checks pass. Retain
headroom beyond observed memory and verify again on the actual host.
