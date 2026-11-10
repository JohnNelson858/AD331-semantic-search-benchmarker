# SearchWorkbench walkthrough

Target 5:30. Start the app and let indexing finish before recording. Keep
your webcam and screen visible throughout. Open the repository, audit
patch, browser, and a second terminal in advance.

| Time | Point and do | Explain |
|---|---|---|
| 0:00–0:55 | Show the README architecture, then `corpus/` and `src/chunking.py`. Point to `FixedSizeChunker` and `StructureAwareChunker`. | The 12 FastAPI chapters supply a realistic search corpus. Fixed token windows overlap. Structural chunks follow headings, except inside code fences. |
| 0:55–2:05 | Open `ai_prompt_log.md`, `docs/audit-baseline-test.txt`, and `docs/audit-fixes.patch`. Point to the MRR cutoff and fence state. | A result below K must score zero. A Python comment must not split a Markdown code example. The same tests fail before and pass after the fixes. |
| 2:05–3:20 | In **Live search**, keep **Structure-aware** and **K=5**. Click **Try exact identifier**, then **Search**. Repeat with **Try conceptual query**. | Explain the `expose_headers` evidence and the synchronous/asynchronous dependencies example. Point to the relevant source excerpt, not just a high score. |
| 3:20–4:50 | Click **Benchmark → Run Benchmark**. Point to the K=5 metrics, encoding latency, and the disagreement panel. | Explain one comparison supported by the actual run, and why rank metrics and lookup timing answer different questions. |
| 4:50–5:30 | Run `uv run --locked pytest -v` in the terminal. Start the suite during the benchmark discussion if needed; leave its result visible at the end. | Point to overlap, fences, BM25 exact match, dense paraphrase and MRR tests. State the observed result and close. |

Check the recorded duration is 5:00–7:00. Upload as Unlisted or Public and
verify playback. Submit the GitHub URL, Render URL if deployed, video link,
corpus and model, and the observed K=5 Hit Rate and MRR for each configuration.
