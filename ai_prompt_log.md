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

## Audit results

The baseline is preserved in Git at commit 654e65b. The failing test output
is in docs/audit-baseline-test.txt and the source diff in docs/audit-fixes.patch.

- **MRR cutoff:** the first relevant rank was looked up in the full list,
  so a result at rank 2 incorrectly earned 0.5 when K was 1. The revised
  calculation only examines the first K results. A miss contributes zero.
- **Fence boundaries:** the structural splitter treated a Python comment
  beginning with a hash as a Markdown heading. It now tracks opening and
  closing fences by character and length and ignores headings inside them.
- **UTF-8 offsets:** decoding incomplete token prefixes can insert replacement
  characters. Fixed windows now calculate offsets from the original token
  bytes and expand display spans to whole Unicode characters. The overlap
  is defined in the original token stream, not by re-tokenizing slices.
- **Label integrity:** labels are unique excerpts in pinned source text,
  resolved into each chunking configuration independently. Query and label
  files are never indexed. An excerpt not covered by any chunk is a miss,
  rather than disappearing from the denominator.
- **Ranking and tokenization:** dense embeddings are normalized and cosine
  distance is converted using 1 − distance. BM25 shares one tokenizer for
  indexing and querying and does not return unmatched filler results.

## Student review before submission

Walk through the original failure output, the patch, and the benchmark
results before recording. The review and presentation should describe what
the observed checks demonstrate and distinguish workspace timing from
measurements taken on your Dell or on Render.
