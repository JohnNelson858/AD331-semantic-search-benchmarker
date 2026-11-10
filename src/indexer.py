"""In-process Chroma cosine collections and BM25."""
import re
import uuid
import chromadb
import numpy as np
from fastembed import TextEmbedding
from rank_bm25 import BM25Okapi
from .model_files import MODEL_ID, prepare
from .search import SearchResult, cosine_score

def lex(text):
    return re.findall(r"[a-z0-9_]+", text.lower())

def unit_rows(values):
    a=np.asarray(values,dtype=np.float32)
    lengths=np.linalg.norm(a,axis=1,keepdims=True)
    if not np.isfinite(a).all() or (lengths <= 0).any():
        raise ValueError("Embeddings must be finite and nonzero")
    return a/lengths

class Encoder:
    def __init__(self):
        self.model=TextEmbedding(MODEL_ID,specific_model_path=str(prepare()),threads=2)
    def embed(self,texts):
        return unit_rows(list(self.model.embed(texts,batch_size=8)))

class Lexical:
    def __init__(self,chunks):
        self.chunks=chunks
        self.tokens=[lex(c.content) for c in chunks]
        self.index=BM25Okapi(self.tokens)
    def search(self,query,k):
        tokens=lex(query)
        present=set(tokens)
        scores=self.index.get_scores(tokens)
        indices=[i for i,doc in enumerate(self.tokens) if present.intersection(doc)]
        indices.sort(key=lambda i:(-float(scores[i]),self.chunks[i].chunk_id))
        return [SearchResult(chunk=self.chunks[i],score=float(scores[i])) for i in indices[:k]]

class Dense:
    def __init__(self,chunks,vectors,client):
        self.chunks={c.chunk_id:c for c in chunks}
        self.collection=client.create_collection("dense-"+uuid.uuid4().hex,configuration={"hnsw":{"space":"cosine","num_threads":2}})
        self.collection.add(ids=list(self.chunks),embeddings=unit_rows(vectors).tolist())
    def search(self,vector,k):
        result=self.collection.query(query_embeddings=unit_rows([vector]).tolist(),n_results=min(k,len(self.chunks)),include=["distances"])
        return [SearchResult(chunk=self.chunks[i],score=cosine_score(d)) for i,d in zip(result["ids"][0],result["distances"][0])]

def memory_client():
    from chromadb.config import Settings
    return chromadb.EphemeralClient(Settings(anonymized_telemetry=False))
