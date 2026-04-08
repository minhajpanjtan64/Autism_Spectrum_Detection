from fastapi import APIRouter

from backend.ai_models.eye_analysis import analyze_eye_metrics
from backend.schemas.eye import EyeAnalyzeRequest, EyeAnalyzeResponse

router = APIRouter(tags=["eye"])


@router.post("/eye/analyze", response_model=EyeAnalyzeResponse)
async def analyze_eye(payload: EyeAnalyzeRequest) -> EyeAnalyzeResponse:
    result = analyze_eye_metrics(payload)
    return EyeAnalyzeResponse(**result)
