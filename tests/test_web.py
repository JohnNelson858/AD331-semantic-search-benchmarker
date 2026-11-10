from fastapi.testclient import TestClient
from src.app import create_app
from src.workbench import Workbench

def test_real_web_search_and_benchmark():
    with TestClient(create_app(Workbench)) as client:
        assert client.get("/healthz").json()=={"status":"ready"}
        assert "Run Benchmark" in client.get("/").text
        assert client.get("/api/info").json()["queries"]==18
        result=client.post("/api/search",json={"query":"expose_headers","k":3}).json()
        assert "expose_headers" in result["bm25"][0]["chunk"]["content"]
        assert len(result["dense"])==3
        assert client.post("/api/search",json={"query":"  "}).status_code==422
        assert client.post("/api/search",json={"query":"example","k":999}).status_code==422
        run=client.post("/api/benchmark",json={}).json()
        assert {row["k"] for row in run["rows"]}=={3,5,10}
        assert len(run["rows"])==12
        assert {f["winner"] for f in run["failures"]}=={"BM25","Dense"}
