from pydantic import BaseModel, Field


class EyeAnalyzeRequest(BaseModel):
    user_id: str
    session_id: str | None = None
    attention_seconds: float = Field(ge=0)
    gaze_stability: float = Field(ge=0, le=1)
    face_presence_ratio: float = Field(ge=0, le=1)
    blink_rate_per_minute: float = Field(ge=0)


class EyeAnalyzeResponse(BaseModel):
    user_id: str
    eye_score: float
    risk_band: str
    confidence: float
    indicators: list[str]
    summary: str
