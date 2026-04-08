from fastapi import APIRouter

from backend.ai_models.speech_analysis import analyze_speech_features
from backend.schemas.speech import SpeechAnalyzeRequest, SpeechAnalyzeResponse

router = APIRouter(tags=["speech"])


@router.post("/speech/analyze", response_model=SpeechAnalyzeResponse)
async def analyze_speech(payload: SpeechAnalyzeRequest) -> SpeechAnalyzeResponse:
    result = analyze_speech_features(payload)
    return SpeechAnalyzeResponse(**result)
