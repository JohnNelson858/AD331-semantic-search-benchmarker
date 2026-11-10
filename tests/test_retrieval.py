import numpy as np
import pytest
from src.chunking import StructureAwareChunker
from src.indexer import Dense, Encoder, Lexical, lex, memory_client, unit_rows

def test_bm25_ranks_exact_identifier_and_ignores_nonmatches():
    chunks=StructureAwareChunker().split("test.md","# General\nUse the feature.\n# Flag\nSet CUSTOM_CONFIG_FLAG_XYZ.")
    idx=Lexical(chunks)
    assert idx.search("custom_config_flag_xyz!",5)[0].chunk.metadata["headers"]==["Flag"]
    assert idx.search("absent_term",5)==[]

def test_cosine_rank_and_sign():
    chunks=StructureAwareChunker().split("test.md","# Match\nA\n# Orthogonal\nB\n# Opposite\nC")
    rows=Dense(chunks,[[2,0],[0,4],[-8,0]],memory_client()).search([5,0],3)
    assert [r.score for r in rows]==pytest.approx([1,0,-1])

@pytest.mark.parametrize("a",[[[0,0]],[[float("nan"),1]]])
def test_invalid_vectors_rejected(a):
    with pytest.raises(ValueError):
        unit_rows(a)

def test_real_model_retrieves_paraphrase_without_lexical_overlap():
    chunks=StructureAwareChunker().split("test.md","# Tasks\nAsynchronous jobs execute once the HTTP response has been sent.\n# Color\nPaint wooden furniture blue.\n# Music\nGuitars have strings.")
    query="Can visitors receive an acknowledgment without waiting for follow-up processing?"
    assert not (set(lex(query)) & set(lex(chunks[0].content)))
    assert Lexical(chunks).search(query,1)==[]
    e=Encoder()
    vectors=e.embed([c.content for c in chunks])
    assert np.allclose(np.linalg.norm(vectors,axis=1),1)
    assert Dense(chunks,vectors,memory_client()).search(e.embed([query])[0],1)[0].chunk.chunk_id==chunks[0].chunk_id
