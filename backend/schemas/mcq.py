from pydantic import BaseModel, Field


class MCQAnswer(BaseModel):
    question_id: str
    answer_value: int = Field(ge=0, le=4)


class MCQSubmitRequest(BaseModel):
    user_id: str | None = None
    questionnaire_id: str = Field(default="screening_v1")
    answers: list[MCQAnswer]


class MCQSubmitResponse(BaseModel):
    user_id: str
    mcq_score: float
    risk_band: str
    confidence: float
    indicators: list[str]
    summary: str
