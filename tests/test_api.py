"""엔드포인트 로직 테스트. Claude 호출은 목킹해 토큰을 쓰지 않는다."""
import pytest
from fastapi.testclient import TestClient

from app import llm, service
from app.main import app

client = TestClient(app)


@pytest.fixture
def mock_llm(monkeypatch):
    """service.generate가 부르는 llm.complete를 고정 문자열로 대체."""
    monkeypatch.setattr(
        llm, "complete", lambda system, user, max_tokens=1024, model=None: "MOCK_RESULT"
    )


def test_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_summarize_text(mock_llm):
    res = client.post("/api/summarize", data={"text": "광합성은 빛으로 양분을 만든다."})
    assert res.status_code == 200
    assert res.json()["result"] == "MOCK_RESULT"


def test_summarize_empty_input_returns_400(mock_llm):
    res = client.post("/api/summarize", data={"text": "   "})
    assert res.status_code == 400


def test_project(mock_llm):
    res = client.post(
        "/api/project",
        json={"members": "강민혜, 김민지", "tasks": "보고서, 발표자료", "deadline": "6/30"},
    )
    assert res.status_code == 200
    assert res.json()["result"] == "MOCK_RESULT"


def test_planner(mock_llm):
    res = client.post(
        "/api/planner",
        json={"exams": "6/25 자료구조 중간", "timetable": "월3", "hours": "3시간"},
    )
    assert res.status_code == 200


def test_search(mock_llm):
    res = client.post("/api/search", json={"query": "과적합을 막는 방법은?"})
    assert res.status_code == 200
    assert res.json()["result"] == "MOCK_RESULT"


def test_search_empty_query_returns_400(mock_llm):
    res = client.post("/api/search", json={"query": "  "})
    assert res.status_code == 400


def test_llm_error_becomes_502(monkeypatch):
    """키 누락 등 LLMError는 502로 변환되어야 한다."""

    def boom(system, user, max_tokens=1024, model=None):
        raise llm.LLMError("ANTHROPIC_API_KEY 없음")

    monkeypatch.setattr(llm, "complete", boom)
    res = client.post("/api/search", json={"query": "테스트"})
    assert res.status_code == 502
    assert "ANTHROPIC_API_KEY" in res.json()["detail"]


def test_llm_missing_key_raises(monkeypatch):
    """환경변수가 없으면 llm.complete가 LLMError를 던진다."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    llm._client.cache_clear()
    with pytest.raises(llm.LLMError):
        llm.complete("s", "u")
    llm._client.cache_clear()
