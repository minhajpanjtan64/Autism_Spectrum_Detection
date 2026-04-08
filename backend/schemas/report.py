from pydantic import BaseModel, Field


class ReportGenerateRequest(BaseModel):
    user_id: str
    eye_score: float = Field(ge=0, le=100)
    speech_score: float = Field(ge=0, le=100)
    mcq_score: float = Field(ge=0, le=100)
    save_pdf: bool = True


class ReportGenerateResponse(BaseModel):
    user_id: str
    final_score: float
    risk_level: str
    recommendation: str
    pdf_path: str | None = None
    report_json: dict
