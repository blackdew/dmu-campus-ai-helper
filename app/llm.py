"""Claude 호출 래퍼.

모든 기능이 이 모듈 하나를 거쳐 Claude를 호출한다.
API 키는 서버 환경변수(ANTHROPIC_API_KEY)에서만 읽으며, 절대 클라이언트로 노출하지 않는다.
"""
import os
from functools import lru_cache

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL = os.getenv("CLAUDE_MODEL", "claude-haiku-4-5")


class LLMError(Exception):
    """키 누락·API 오류 등 Claude 호출 실패를 사용자에게 전달하기 위한 예외."""


@lru_cache(maxsize=1)
def _client() -> Anthropic:
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        raise LLMError(
            "ANTHROPIC_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요 (.env.example 참고)."
        )
    return Anthropic(api_key=key)


def complete(system: str, user: str, max_tokens: int = 1024, model: str | None = None) -> str:
    """system/user 프롬프트로 Claude를 호출하고 텍스트 응답을 반환한다."""
    try:
        resp = _client().messages.create(
            model=model or DEFAULT_MODEL,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
    except LLMError:
        raise
    except Exception as exc:  # SDK/네트워크 오류를 LLMError로 표준화
        raise LLMError(f"Claude 호출에 실패했습니다: {exc}") from exc

    return "".join(block.text for block in resp.content if getattr(block, "type", None) == "text")
