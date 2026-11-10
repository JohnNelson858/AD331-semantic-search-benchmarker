import pytest
from src.chunking import FixedSizeChunker, StructureAwareChunker, tokenizer

def test_overlap_preserves_original_token_windows():
    text=" ".join(f"entry {i:03d}" for i in range(75))
    enc=tokenizer()
    original=enc.encode_ordinary(text)
    chunks=FixedSizeChunker(24,6).split("test.md",text)
    for c in chunks:
        a,b=(c.metadata[k] for k in ("token_start","token_end"))
        assert c.content==enc.decode(original[a:b])
    assert all(a.metadata["token_end"]-b.metadata["token_start"]==6 for a,b in zip(chunks,chunks[1:]))
    assert chunks[-1].metadata["end"]==len(text)

def test_unicode_spans_never_drop_characters():
    text="A😀 café 漢字 🧪"
    chunks=FixedSizeChunker(1,0).split("test.md",text)
    assert all(c.content==text[c.metadata["start"]:c.metadata["end"]] for c in chunks)
    assert set().union(*(set(range(c.metadata["start"],c.metadata["end"])) for c in chunks))==set(range(len(text)))

@pytest.mark.parametrize("fence",["```","~~~~"])
def test_structural_fence_and_parent_headers(fence):
    text=f"# Topic\n## API\n{fence}python\n# pseudo header\n{fence}\n### Return\nResult."
    chunks=StructureAwareChunker().split("test.md",text)
    assert chunks[1].metadata["headers"]==["Topic","API"]
    assert "# pseudo header" in chunks[1].content
    assert chunks[2].metadata["headers"]==["Topic","API","Return"]

def test_html_headings_and_preformatted_code(tmp_path):
    from src.ingest import read_document
    p=tmp_path/"api.html"
    p.write_text("<h1>API</h1><p>Intro</p><h2>Usage</h2><pre># a comment\nx = 1 &lt; 2</pre><script>ignored</script>",encoding="utf-8")
    chunks=StructureAwareChunker().split(p.name,read_document(p))
    assert len(chunks)==2
    assert chunks[1].metadata["headers"]==["API","Usage"]
    assert "# a comment\nx = 1 < 2" in chunks[1].content
    assert "ignored" not in chunks[1].content
