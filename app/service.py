"""라우터와 LLM 래퍼 사이의 얇은 어댑터.

llm.LLMError를 HTTP 502 응답으로 변환해, 각 라우터가 같은 try/except를 반복하지 않게 한다.
"""
from fastapi import HTTPException

from app import llm


def generate(system: str, user: str, max_tokens: int = 1024) -> str:
    try:
        return llm.complete(system, user, max_tokens=max_tokens)
    except llm.LLMError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
