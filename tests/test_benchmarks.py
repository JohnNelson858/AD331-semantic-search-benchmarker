import pytest
from src.benchmarker import QueryCase, metrics, resolve
from src.chunking import StructureAwareChunker

def test_metrics_count_source_evidence_not_duplicate_chunks():
    groups=[{"a","b"},{"c"}]
    assert metrics(["z","a","b","c"],groups,3)=={"hit_rate":1.0,"recall":0.5,"mrr":0.5}
    assert metrics(["z","a","b","c"],groups,4)["recall"]==1
    assert metrics(["z","a","b","c"],groups,1)=={"hit_rate":0,"recall":0,"mrr":0}

def test_missing_coverage_remains_in_denominator():
    assert metrics(["a"],[{"a"},set()],5)["recall"]==0.5

def test_source_label_rejects_ambiguity():
    source="# A\nneedle\n# B\nneedle\n"
    case=QueryCase(id="test",kind="exact",query="needle",evidence=[{"doc":"a.md","quote":"needle"}])
    with pytest.raises(ValueError,match="exactly once"):
        resolve(case,{"a.md":source},StructureAwareChunker().split("a.md",source))
