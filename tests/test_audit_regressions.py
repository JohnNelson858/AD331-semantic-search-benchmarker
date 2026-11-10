from src.benchmarker import metrics
from src.chunking import StructureAwareChunker

def test_mrr_does_not_credit_relevance_outside_k():
    assert metrics(["irrelevant","correct"],[{"correct"}],1)["mrr"] == 0.0

def test_heading_inside_code_fence_is_not_a_boundary():
    text="# Intro\n\n```python\n# comment\nx = 1\n```\n\n## More\nText\n"
    chunks=StructureAwareChunker().split("sample.md",text)
    assert len(chunks)==2
    assert "```python\n# comment\nx = 1\n```" in chunks[0].content
