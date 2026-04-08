from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter

from backend.ai_models.risk_engine import compute_final_risk
from backend.schemas.report import ReportGenerateRequest, ReportGenerateResponse
from backend.services.pdf_generator import generate_pdf_report

router = APIRouter(tags=["report"])


@router.post("/generate-report", response_model=ReportGenerateResponse)
async def generate_report(payload: ReportGenerateRequest) -> ReportGenerateResponse:
    report = compute_final_risk(payload.eye_score, payload.speech_score, payload.mcq_score)
    report_json = {
        "user_id": payload.user_id,
        "eye_score": payload.eye_score,
        "speech_score": payload.speech_score,
        "mcq_score": payload.mcq_score,
        "final_score": report["final_score"],
        "risk_level": report["risk_level"],
        "recommendation": report["recommendation"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    pdf_path = None
    if payload.save_pdf:
        pdf_path = generate_pdf_report(report_json, str(Path("reports") / f"report_{payload.user_id}.pdf"))

    return ReportGenerateResponse(
        user_id=payload.user_id,
        final_score=report["final_score"],
        risk_level=report["risk_level"],
        recommendation=report["recommendation"],
        pdf_path=pdf_path,
        report_json=report_json,
    )
