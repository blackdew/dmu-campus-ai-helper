"""동명대 AI 프로젝트 도우미 — FastAPI 단일 앱.

정적 프런트(/)와 JSON API(/api/*)를 한 서버가 함께 서빙한다.
"""
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers import planner, project, search, summarize

app = FastAPI(title="동명대 AI 프로젝트 도우미")

# API 라우터를 정적 마운트보다 먼저 등록한다 (정적 마운트가 "/"를 모두 잡으므로).
app.include_router(summarize.router)
app.include_router(project.router)
app.include_router(planner.router)
app.include_router(search.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}


STATIC_DIR = Path(__file__).parent / "static"
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
