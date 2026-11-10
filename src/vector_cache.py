"""Content-addressed corpus embeddings baked into the deployment image.

These are real model outputs, not fixture search results. Queries are always
encoded live. A changed corpus/model invalidates the cache automatically.
"""
import hashlib
import json
import os
from pathlib import Path
import numpy as np
from .model_files import MODEL_ID, REVISION


def corpus_vectors(chunks,encoder):
    directory=os.getenv("VECTOR_CACHE_DIR")
    required=os.getenv("VECTOR_CACHE_REQUIRED","0")=="1"
    if required and not directory:
        raise RuntimeError("VECTOR_CACHE_REQUIRED needs VECTOR_CACHE_DIR")
    fingerprint=hashlib.sha256(json.dumps({
        "format":1,"model":MODEL_ID,"revision":REVISION,
        "chunks":[{"id":c.chunk_id,"content":c.content} for c in chunks],
    },sort_keys=True,ensure_ascii=False).encode("utf-8")).hexdigest()
    target=Path(directory)/f"{fingerprint}.npy" if directory else None
    if target is not None and target.is_file():
        vectors=np.load(target,allow_pickle=False)
        if (vectors.shape!=(len(chunks),512) or vectors.dtype!=np.float32
                or not np.isfinite(vectors).all()
                or not np.allclose(np.linalg.norm(vectors,axis=1),1,atol=1e-5)):
            raise ValueError("Invalid corpus embedding cache; rebuild the image")
        return vectors
    if required:
        raise RuntimeError("Corpus embedding cache missing or stale; rebuild the image")
    vectors=encoder.embed([c.content for c in chunks])
    if target is not None:
        target.parent.mkdir(parents=True,exist_ok=True)
        part=target.with_suffix(".tmp")
        with part.open("wb") as output:
            np.save(output,vectors,allow_pickle=False)
        part.replace(target)
    return vectors


if __name__=="__main__":
    from .workbench import Workbench
    if not os.getenv("VECTOR_CACHE_DIR"):
        raise SystemExit("Set VECTOR_CACHE_DIR before building the corpus embedding cache")
    Workbench()
    print("Corpus embeddings ready for all three dense strategies.")
