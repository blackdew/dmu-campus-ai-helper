"""#5 스터디 플래너 챗봇 — 시험일정·시간표 → 학습 스케줄 + 우선순위."""
from fastapi import APIRouter
from pydantic import BaseModel

from app import service

router = APIRouter(prefix="/api")

SYSTEM = "당신은 대학생의 학습 계획을 돕는 스터디 플래너입니다. 한국어로 구체적인 일정으로 답하세요."


class PlannerIn(BaseModel):
    exams: str  # 시험/과제 일정
    timetable: str = ""  # 시간표 (선택)
    hours: str = ""  # 하루 가용 학습 시간 (선택)


@router.post("/planner")
def planner(body: PlannerIn):
    user = (
        f"시험/과제 일정: {body.exams}\n"
        f"시간표: {body.timetable or '미입력'}\n"
        f"하루 가용 학습 시간: {body.hours or '미입력'}\n\n"
        "요청:\n"
        "1) 시험일 역산 기반 일자별 학습 스케줄\n"
        "2) 과목/과제 우선순위와 그 이유\n"
        "3) 막판 벼락치기를 피하기 위한 팁"
    )
    return {"result": service.generate(SYSTEM, user, max_tokens=1200)}
