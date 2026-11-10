"""Source-preserving Markdown splitters with stable line coordinates."""
import re
from functools import lru_cache
import tiktoken
from pydantic import BaseModel

@lru_cache(maxsize=1)
def tokenizer():
    return tiktoken.get_encoding("cl100k_base")

class DocumentChunk(BaseModel):
    chunk_id: str
    content: str
    parent_doc: str
    metadata: dict

def make_chunk(doc, text, start, end, ordinal, header):
    return DocumentChunk(chunk_id=f"{doc}:{ordinal:04d}", content=text[start:end], parent_doc=doc,
        metadata={"start":start,"end":end,"start_line":text.count("\n",0,start)+1,
                  "end_line":text.count("\n",0,max(start,end-1))+1,
                  "headers":header,"tokens":len(tokenizer().encode_ordinary(text[start:end]))})

class FixedSizeChunker:
    def __init__(self, chunk_size: int, chunk_overlap: int):
        if not 0 <= chunk_overlap < chunk_size:
            raise ValueError("Require 0 <= overlap < size")
        self.size, self.overlap = chunk_size, chunk_overlap

    def split(self, doc: str, text: str) -> list[DocumentChunk]:
        enc=tokenizer()
        ids=enc.encode_ordinary(text)
        stride=self.size-self.overlap
        out=[]
        for i in range(0,len(ids),stride):
            j=min(i+self.size,len(ids))
            start=len(enc.decode(ids[:i]))
            end=len(enc.decode(ids[:j]))
            out.append(make_chunk(doc,text,start,end,len(out),[]))
            if j==len(ids):
                break
        return out

HEADING=re.compile(r"^ {0,3}(#{1,6})\s+(.+?)\s*$")
FENCE=re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")

class StructureAwareChunker:
    def split(self, doc: str, text: str) -> list[DocumentChunk]:
        headers=[]; out=[]; offset=start=0
        for line in text.splitlines(keepends=True):
            match=HEADING.match(line.rstrip("\r\n"))
            if match:
                if text[start:offset].strip():
                    out.append(make_chunk(doc,text,start,offset,len(out),[v for _,v in headers]))
                level=len(match[1])
                headers=[x for x in headers if x[0]<level]+[(level,match[2])]
                start=offset
            offset+=len(line)
        if text[start:].strip():
            out.append(make_chunk(doc,text,start,len(text),len(out),[v for _,v in headers]))
        return out
