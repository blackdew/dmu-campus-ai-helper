"""LLM 호출 래퍼 (OpenAI).

모든 기능이 이 모듈 하나를 거쳐 LLM을 호출한다.
API 키는 서버 환경변수(OPENAI_API_KEY)에서만 읽으며, 절대 클라이언트로 노출하지 않는다.
"""
import os
from functools import lru_cache

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


class LLMError(Exception):
    """키 누락·API 오류 등 LLM 호출 실패를 사용자에게 전달하기 위한 예외."""


@lru_cache(maxsize=1)
def _client() -> OpenAI:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise LLMError(
            "OPENAI_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요 (.env.example 참고)."
        )
    return OpenAI(api_key=key)


def complete(system: str, user: str, max_tokens: int = 1024, model: str | None = None) -> str:
    """system/user 프롬프트로 LLM을 호출하고 텍스트 응답을 반환한다."""
    try:
        resp = _client().chat.completions.create(
            model=model or DEFAULT_MODEL,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
    except LLMError:
        raise
    except Exception as exc:  # SDK/네트워크 오류를 LLMError로 표준화
        raise LLMError(f"LLM 호출에 실패했습니다: {exc}") from exc

    return resp.choices[0].message.content or ""
