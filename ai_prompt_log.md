# AI generation and verification log

## Initial generation prompt

Build an AD 331 Python 3.11+ technical document retrieval workbench. Use a pinned
FastAPI documentation corpus, token windows at 256 and 1024 tokens, and
Markdown header splitting with fence preservation. Return typed chunks with
source offsets and hierarchy. Implement embedded Chroma cosine search and
BM25 with symmetric tokenization. Map evaluation labels from stable source
excerpts to each strategy's chunks. Report Hit Rate, Recall and MRR at 3, 5 and
10 and retrieval latency. Keep query embedding cost visible separately.
Use a local embedding model, a side-by-side FastAPI UI and a Docker packaging
path for Render. Audit the generated baseline and test fixes with regressions.
