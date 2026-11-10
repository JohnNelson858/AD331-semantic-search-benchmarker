"""Relevance labels point to immutable evidence excerpts in source files."""
from pydantic import BaseModel

class Evidence(BaseModel):
    doc: str
    quote: str

class QueryCase(BaseModel):
    id: str
    kind: str
    query: str
    evidence: list[Evidence]

def resolve(case,corpus,chunks):
    groups=[]
    for evidence in case.evidence:
        source=corpus[evidence.doc]
        if source.count(evidence.quote)!=1:
            raise ValueError(f"{case.id}: evidence must occur exactly once in {evidence.doc}")
        start=source.index(evidence.quote)
        end=start+len(evidence.quote)
        groups.append({c.chunk_id for c in chunks if c.parent_doc==evidence.doc
                       and c.metadata["start"]<=start and c.metadata["end"]>=end})
    return groups

def metrics(ranking, groups, k):
    top=set(ranking[:k])
    count=sum(bool(g & top) for g in groups)
    relevant=set().union(*groups)
    first=next((i for i,x in enumerate(ranking[:k],1) if x in relevant),0)
    return {"hit_rate":float(count>0),"recall":count/len(groups),"mrr":1/first if first else 0.0}
