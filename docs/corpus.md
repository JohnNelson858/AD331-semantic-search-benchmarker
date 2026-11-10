# Corpus provenance

The Markdown source is from FastAPI 0.115.6, distributed under the upstream
MIT license included at `corpus/LICENSE`. The original chapters are under
`docs/en/docs/tutorial/` in the upstream repository. The local
`dependencies.md` came from `dependencies/index.md`. FastAPI's MkDocs
code-inclusion markers were expanded into fenced Python snippets taken from
`docs_src/` at the same release. This keeps the examples searchable without
requiring the upstream documentation builder.

Source: https://github.com/fastapi/fastapi/tree/0.115.6/docs/en/docs/tutorial

For the demo, headings and line ranges refer to the local expanded snapshot.
The project does not execute examples found in the corpus.

Dense model: Jina Embeddings v2 small English, ONNX conversion by Xenova.
https://huggingface.co/Xenova/jina-embeddings-v2-small-en/tree/523cadcb9c2e71c7153fc46016e1fe79acb4f58f

The observed longest inputs, counted with the model tokenizer before
truncation, were 372 tokens for the 256-token windows, 1,372 for the
1,024-token windows, and 3,248 for structure-aware chunks. All fit under the
model tokenizer's 8,192-token limit. These counts differ from cl100k_base
because the model uses a different tokenizer.
