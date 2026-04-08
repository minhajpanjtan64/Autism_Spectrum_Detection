from fastapi import APIRouter

from backend.ai_models.risk_engine import compute_final_risk
from backend.schemas.mcq import MCQSubmitRequest, MCQSubmitResponse

router = APIRouter(tags=["mcq"])


@router.post("/mcq/submit", response_model=MCQSubmitResponse)
async def submit_mcq(payload: MCQSubmitRequest) -> MCQSubmitResponse:
    if not payload.answers:
        mcq_score = 0.0
    else:
        total = sum(answer.answer_value for answer in payload.answers)
        max_total = len(payload.answers) * 4
        mcq_score = round(((total / max_total) * 100.0) if max_total else 0.0, 2)

    # Convert score to the same convention used by the fusion engine.
    normalized_score = round(100.0 - mcq_score, 2)
    _ = compute_final_risk(normalized_score, normalized_score, normalized_score)

    if normalized_score >= 75:
        risk_band = "low"
    elif normalized_score >= 50:
        risk_band = "moderate"
    else:
        risk_band = "high"

    return MCQSubmitResponse(
        user_id=payload.user_id,
        mcq_score=normalized_score,
        risk_band=risk_band,
        confidence=0.70,
        indicators=["questionnaire_scored"],
        summary="MCQ screening submitted successfully.",
    )
