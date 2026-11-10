"""Build once, serve read-only indexes, and evaluate real rankings."""
import json
from pathlib import Path
from time import perf_counter
import numpy as np

from .benchmarker import QueryCase, metrics, resolve
from .chunking import FixedSizeChunker, StructureAwareChunker
from .indexer import Dense, Encoder, Lexical, lex, memory_client
from .ingest import read_document

ROOT = Path(__file__).resolve().parents[1]
CONFIGS = {"fixed256": "Dense · 256 tokens", "fixed1024": "Dense · 1024 tokens",
           "structural": "Dense · structure-aware"}

class Workbench:
    def __init__(self, encoder=None):
        self.corpus={p.name:read_document(p) for p in sorted((ROOT/"corpus").iterdir())
                     if p.suffix.lower() in {".md",".html",".htm"}}
        self.cases=[QueryCase.model_validate(d) for d in json.loads((ROOT/"data/eval_queries.json").read_text(encoding="utf-8"))]
        self.encoder=encoder or Encoder()
        self.chunks={}
        self.dense={}
        self.client=memory_client()
        for key,splitter in (("fixed256",FixedSizeChunker(256,32)),("fixed1024",FixedSizeChunker(1024,128)),
                             ("structural",StructureAwareChunker())):
            chunks=[c for doc,text in self.corpus.items() for c in splitter.split(doc,text)]
            self.chunks[key]=chunks
            self.dense[key]=Dense(chunks,self.encoder.embed([c.content for c in chunks]),self.client)
        self.lexical=Lexical(self.chunks["structural"])
        self.chunks["bm25"]=self.chunks["structural"]
        self.ground_truth={key:{q.id:resolve(q,self.corpus,cs) for q in self.cases}
                           for key,cs in self.chunks.items()}

    def compare(self,query,k,strategy):
        start=perf_counter(); lexical=self.lexical.search(query,k); lex_ms=(perf_counter()-start)*1000
        start=perf_counter(); vector=self.encoder.embed([query])[0]; embed_ms=(perf_counter()-start)*1000
        start=perf_counter(); dense=self.dense[strategy].search(vector,k); dense_ms=(perf_counter()-start)*1000
        return {"bm25":lexical,"dense":dense,"timings":{"bm25":lex_ms,"dense":dense_ms,"embedding":embed_ms}}

    def benchmark(self):
        stats={key:[] for key in self.chunks}
        failures=[]
        k_values=(3,5,10)
        for q in self.cases:
            start=perf_counter()
            v=self.encoder.embed([q.query])[0]
            embed_ms=(perf_counter()-start)*1000
            ranks={}
            for key in self.chunks:
                start=perf_counter()
                result=self.lexical.search(q.query,10) if key=="bm25" else self.dense[key].search(v,10)
                elapsed=(perf_counter()-start)*1000
                ranking=[r.chunk.chunk_id for r in result]
                groups=self.ground_truth[key][q.id]
                scored={str(k):metrics(ranking,groups,k) for k in k_values}
                ranks[key]=scored["5"]["mrr"]
                stats[key].append((elapsed,embed_ms if key!="bm25" else 0,scored))
            if ranks["bm25"]!=ranks["structural"]:
                better="BM25" if ranks["bm25"]>ranks["structural"] else "Dense"
                shared=sorted(set(lex(q.query)) & set(lex(" ".join(e.quote for e in q.evidence))))
                overlap=", ".join(shared) or "none"
                hint=f"Query terms in the labeled evidence: {overlap}. This is a clue, not a causal test."
                evidence=[{"doc":e.doc,"quote":e.quote} for e in q.evidence]
                failures.append({"id":q.id,"query":q.query,"kind":q.kind,"winner":better,
                                 "bm25":ranks["bm25"],"dense":ranks["structural"],"hint":hint,"evidence":evidence})
        rows=[]
        for key,measurements in stats.items():
            ms=[t[0] for t in measurements]
            for k in k_values:
                measures=[m[2][str(k)] for m in measurements]
                rows.append({"strategy":key,"name":"BM25 · structure-aware" if key=="bm25" else CONFIGS[key],
                    "k":k,"chunk_count":len(self.chunks[key]),
                    **{x:float(np.mean([m[x] for m in measures])) for x in ("hit_rate","recall","mrr")},
                    "avg_ms":float(np.mean(ms)),"p50_ms":float(np.percentile(ms,50)),
                    "p95_ms":float(np.percentile(ms,95)),"embedding_ms":float(np.mean([t[1] for t in measurements]))})
        return {"queries":len(self.cases),"rows":rows,"failures":failures,
                "latency_scope":"Search at K=10 after indexing; dense query embedding reported separately."}

if __name__=="__main__":
    print(json.dumps(Workbench().benchmark(),indent=2))
