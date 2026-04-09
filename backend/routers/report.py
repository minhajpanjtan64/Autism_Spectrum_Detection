from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException

from backend.ai_models.risk_engine import compute_final_risk
from backend.dependencies.auth import AuthUser, get_current_user, resolve_user_id
from backend.schemas.report import ReportGenerateRequest, ReportGenerateResponse
from backend.services.assessment_store import get_latest_scores, save_report
from backend.services.pdf_generator import generate_pdf_report

router = APIRouter(tags=["report"])


@router.post("/generate-report", response_model=ReportGenerateResponse)
async def generate_report(
    payload: ReportGenerateRequest,
    auth_user: AuthUser = Depends(get_current_user),
) -> ReportGenerateResponse:
    user_id = resolve_user_id(payload.user_id, auth_user)
    saved_scores = get_latest_scores(user_id)

    eye_score = payload.eye_score
    speech_score = payload.speech_score
    mcq_score = payload.mcq_score

    if payload.use_saved_scores:
        eye_score = eye_score if eye_score is not None else saved_scores["eye_score"]
        speech_score = speech_score if speech_score is not None else saved_scores["speech_score"]
        mcq_score = mcq_score if mcq_score is not None else saved_scores["mcq_score"]

    if eye_score is None or speech_score is None or mcq_score is None:
        raise HTTPException(
            status_code=400,
            detail="Missing score values. Submit eye, speech, and MCQ modules first or provide all scores.",
        )

    report = compute_final_risk(eye_score, speech_score, mcq_score)
    report_json = {
        "user_id": user_id,
        "eye_score": eye_score,
        "speech_score": speech_score,
        "mcq_score": mcq_score,
        "final_score": report["final_score"],
        "risk_level": report["risk_level"],
        "recommendation": report["recommendation"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    pdf_path = None
    if payload.save_pdf:
        pdf_path = generate_pdf_report(report_json, str(Path("reports") / f"report_{user_id}.pdf"))

    save_report(user_id, report_json, pdf_path)

    return ReportGenerateResponse(
        user_id=user_id,
        final_score=report["final_score"],
        risk_level=report["risk_level"],
        recommendation=report["recommendation"],
        pdf_path=pdf_path,
        report_json=report_json,
    )
