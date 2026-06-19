"""#4 캠퍼스 프로젝트 도우미 — 팀원·과제·마감 → 역할 배분 + 일정 + 마감 요약."""
from fastapi import APIRouter
from pydantic import BaseModel

from app import service

router = APIRouter(prefix="/api")

SYSTEM = "당신은 대학생 팀 프로젝트를 돕는 PM 코치입니다. 한국어로 실용적으로 답하세요."


class ProjectIn(BaseModel):
    members: str  # 팀원 (쉼표 구분 등 자유 형식)
    tasks: str  # 할 일/과제
    deadline: str = ""  # 마감일 (선택)


@router.post("/project")
def project(body: ProjectIn):
    user = (
        f"팀원: {body.members}\n"
        f"할 일/과제: {body.tasks}\n"
        f"마감일: {body.deadline or '미정'}\n\n"
        "요청:\n"
        "1) 팀원별 역할 배분 추천 (각자 맡을 부분과 이유)\n"
        "2) 마감까지 단계별 일정 (주차 또는 날짜 단위)\n"
        "3) 마감 임박 시 주의할 점 요약"
    )
    return {"result": service.generate(SYSTEM, user, max_tokens=1200)}
