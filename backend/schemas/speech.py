from pydantic import BaseModel, Field


class SpeechAnalyzeRequest(BaseModel):
    user_id: str
    session_id: str | None = None
    audio_duration_seconds: float = Field(ge=0)
    transcript_text: str | None = None
    voice_variability: float = Field(ge=0, le=1)
    pause_ratio: float = Field(ge=0, le=1)


class SpeechAnalyzeResponse(BaseModel):
    user_id: str
    speech_score: float
    risk_band: str
    confidence: float
    indicators: list[str]
    summary: str
