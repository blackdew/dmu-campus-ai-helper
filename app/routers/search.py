"""#6 맞춤형 자료 검색 AI — 번들된 샘플 강의자료에서 답변 + 출처.

데모는 벡터DB/임베딩 없이 '관련 문서를 컨텍스트로 주입'하는 방식이다(YAGNI).
실서비스는 임베딩 기반 RAG로 확장한다.
"""
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app import service

router = APIRouter(prefix="/api")

SAMPLES_DIR = Path(__file__).resolve().parents[2] / "data" / "samples"
MAX_CONTEXT_CHARS = 12000

SYSTEM = (
    "당신은 강의자료 기반 질의응답 도우미입니다. 제공된 자료에 근거해서만 한국어로 답하고, "
    "사용한 근거는 [출처: 파일명] 형식으로 표기하세요. 자료에 없으면 모른다고 솔직히 답하세요."
)


class SearchIn(BaseModel):
    query: str


def _load_corpus() -> list[tuple[str, str]]:
    if not SAMPLES_DIR.exists():
        return []
    return [(p.name, p.read_text(encoding="utf-8")) for p in sorted(SAMPLES_DIR.glob("*.txt"))]


@router.post("/search")
def search(body: SearchIn):
    query = body.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="검색할 질문을 입력하세요.")

    corpus = _load_corpus()
    if not corpus:
        raise HTTPException(status_code=503, detail="검색할 샘플 자료가 없습니다.")

    context = "\n\n".join(f"[출처: {name}]\n{text}" for name, text in corpus)
    user = (
        "다음 강의자료를 참고해 질문에 답하고, 사용한 출처를 표기해줘.\n\n"
        f"=== 자료 ===\n{context[:MAX_CONTEXT_CHARS]}\n\n"
        f"=== 질문 ===\n{query}"
    )
    return {"result": service.generate(SYSTEM, user, max_tokens=1000)}
