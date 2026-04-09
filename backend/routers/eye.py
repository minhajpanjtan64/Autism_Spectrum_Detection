from fastapi import APIRouter, Depends

from backend.ai_models.eye_analysis import analyze_eye_metrics
from backend.dependencies.auth import AuthUser, get_current_user, resolve_user_id
from backend.schemas.eye import EyeAnalyzeRequest, EyeAnalyzeResponse
from backend.services.assessment_store import update_module_result

router = APIRouter(tags=["eye"])


@router.post("/eye/analyze", response_model=EyeAnalyzeResponse)
async def analyze_eye(payload: EyeAnalyzeRequest, auth_user: AuthUser = Depends(get_current_user)) -> EyeAnalyzeResponse:
    user_id = resolve_user_id(payload.user_id, auth_user)
    payload.user_id = user_id
    result = analyze_eye_metrics(payload)
    update_module_result(user_id, "eye", result["eye_score"])
    return EyeAnalyzeResponse(**result)
