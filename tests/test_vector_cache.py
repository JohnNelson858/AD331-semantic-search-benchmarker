import numpy as np
import pytest
from src.chunking import StructureAwareChunker
from src.vector_cache import corpus_vectors


class CountingEncoder:
    def __init__(self):
        self.calls=0

    def embed(self,texts):
        self.calls+=1
        return np.full((len(texts),512),1/np.sqrt(512),dtype=np.float32)


def test_cache_reuses_vectors_and_invalidates_changed_source(tmp_path,monkeypatch):
    monkeypatch.setenv("VECTOR_CACHE_DIR",str(tmp_path))
    monkeypatch.setenv("VECTOR_CACHE_REQUIRED","0")
    encoder=CountingEncoder()
    splitter=StructureAwareChunker()
    chunks=splitter.split("test.md","# Topic\nOriginal document.")
    original=corpus_vectors(chunks,encoder)
    assert np.array_equal(original,corpus_vectors(chunks,encoder))
    assert encoder.calls==1
    changed=splitter.split("test.md","# Topic\nChanged document.")
    monkeypatch.setenv("VECTOR_CACHE_REQUIRED","1")
    with pytest.raises(RuntimeError,match="missing or stale"):
        corpus_vectors(changed,encoder)
    # Required deployment caches must never silently trigger large inference.
    assert encoder.calls==1
    monkeypatch.setenv("VECTOR_CACHE_REQUIRED","0")
    corpus_vectors(changed,encoder)
    assert encoder.calls==2
    assert len(list(tmp_path.glob("*.npy")))==2


def test_invalid_cached_vectors_are_rejected(tmp_path,monkeypatch):
    monkeypatch.setenv("VECTOR_CACHE_DIR",str(tmp_path))
    monkeypatch.setenv("VECTOR_CACHE_REQUIRED","0")
    chunks=StructureAwareChunker().split("test.md","# Topic\nA document.")
    encoder=CountingEncoder()
    corpus_vectors(chunks,encoder)
    np.save(next(tmp_path.glob("*.npy")),np.zeros((len(chunks),512),dtype=np.float32))
    with pytest.raises(ValueError,match="Invalid corpus embedding cache"):
        corpus_vectors(chunks,encoder)
    assert encoder.calls==1
