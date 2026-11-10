"""FastAPI dashboard for the AD 331 retrieval workbench."""
import asyncio
from contextlib import asynccontextmanager
from threading import BoundedSemaphore, Lock
from typing import Literal
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from .workbench import CONFIGS, ROOT, Workbench

class SearchRequest(BaseModel):
    query: str = Field(min_length=1,max_length=400)
    k: int = Field(default=5,ge=1,le=10)
    strategy: Literal["fixed256","fixed1024","structural"] = "structural"

def create_app(builder=Workbench):
    @asynccontextmanager
    async def lifespan(app):
        app.state.workbench=await asyncio.to_thread(builder)
        yield
    app=FastAPI(title="SearchWorkbench",lifespan=lifespan)
    static=ROOT/"src/static"
    app.mount("/static",StaticFiles(directory=static),name="static")
    search_slots=BoundedSemaphore(2)
    benchmark_slot=Lock()

    @app.get("/")
    def home():
        return FileResponse(static/"index.html")

    @app.get("/healthz")
    def health():
        return {"status":"ready"}

    @app.get("/api/info")
    def info():
        w=app.state.workbench
        return {"documents":len(w.corpus),"queries":len(w.cases),"strategies":CONFIGS,
                "examples":[{"query":q.query,"kind":q.kind} for q in w.cases if q.id in {"q08","q16"}]}

    @app.post("/api/search")
    def search(body: SearchRequest):
        if not body.query.strip():
            raise HTTPException(422,"Enter a nonblank query.")
        if not search_slots.acquire(blocking=False):
            raise HTTPException(429,"Search is busy. Try again shortly.")
        try:
            return app.state.workbench.compare(body.query.strip(),body.k,body.strategy)
        finally:
            search_slots.release()

    @app.post("/api/benchmark")
    def benchmark():
        if not benchmark_slot.acquire(blocking=False):
            raise HTTPException(429,"A benchmark is already running.")
        try:
            return app.state.workbench.benchmark()
        finally:
            benchmark_slot.release()
    return app

app=create_app()
