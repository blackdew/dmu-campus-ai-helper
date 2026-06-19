"""#3 강의자료 요약 AI — PDF/텍스트 → 핵심요약 + 퀴즈 + 포인트."""
from io import BytesIO

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pypdf import PdfReader

from app import service

router = APIRouter(prefix="/api")

MAX_BYTES = 5 * 1024 * 1024  # 5MB
MAX_CHARS = 12000  # 프롬프트에 넣을 본문 상한

SYSTEM = "당신은 대학생의 학습을 돕는 조교입니다. 한국어로 명확하고 간결하게 답하세요."


def _extract_pdf(data: bytes) -> str:
    try:
        reader = PdfReader(BytesIO(data))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as exc:  # 깨진 PDF 등
        raise HTTPException(status_code=400, detail="PDF를 읽을 수 없습니다.") from exc


@router.post("/summarize")
async def summarize(text: str = Form(default=""), file: UploadFile | None = File(default=None)):
    content = (text or "").strip()

    if file is not None:
        data = await file.read()
        if len(data) > MAX_BYTES:
            raise HTTPException(status_code=413, detail="파일이 너무 큽니다 (최대 5MB).")
        content = _extract_pdf(data).strip()

    if not content:
        raise HTTPException(status_code=400, detail="요약할 텍스트나 PDF를 입력하세요.")

    user = (
        "다음 강의자료를 학습용으로 정리해줘.\n"
        "1) 핵심 요약 — 불릿 5개 내외\n"
        "2) 객관식 퀴즈 3개 — 보기와 정답 포함\n"
        "3) 시험 대비 핵심 포인트\n\n"
        f"=== 강의자료 ===\n{content[:MAX_CHARS]}"
    )
    return {"result": service.generate(SYSTEM, user, max_tokens=1500)}
