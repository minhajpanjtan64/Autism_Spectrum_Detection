from fastapi import APIRouter, Depends

from backend.ai_models.risk_engine import compute_final_risk
from backend.dependencies.auth import AuthUser, get_current_user, resolve_user_id
from backend.schemas.mcq import MCQSubmitRequest, MCQSubmitResponse
from backend.services.assessment_store import update_module_result

router = APIRouter(tags=["mcq"])


@router.post("/mcq/submit", response_model=MCQSubmitResponse)
async def submit_mcq(payload: MCQSubmitRequest, auth_user: AuthUser = Depends(get_current_user)) -> MCQSubmitResponse:
    user_id = resolve_user_id(payload.user_id, auth_user)

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

    update_module_result(user_id, "mcq", normalized_score)

    return MCQSubmitResponse(
        user_id=user_id,
        mcq_score=normalized_score,
        risk_band=risk_band,
        confidence=0.70,
        indicators=["questionnaire_scored"],
        summary="MCQ screening submitted successfully.",
    )
