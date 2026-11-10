"""Comparable result shape for the two search engines."""
from pydantic import BaseModel
from .chunking import DocumentChunk

class SearchResult(BaseModel):
    chunk: DocumentChunk
    score: float

def cosine_score(distance: float) -> float:
    return 1.0 - distance
