from __future__ import annotations

from backend.schemas.eye import EyeAnalyzeRequest


def analyze_eye_metrics(payload: EyeAnalyzeRequest) -> dict:
    """Rule-based eye tracking baseline for early screening.

    This starter implementation uses simple heuristics and is intended to be
    replaced later with MediaPipe-based feature extraction.
    """

    attention_component = min(payload.attention_seconds / 60.0, 1.0) * 40.0
    stability_component = payload.gaze_stability * 35.0
    presence_component = payload.face_presence_ratio * 15.0
    blink_component = max(0.0, 10.0 - min(payload.blink_rate_per_minute / 3.0, 10.0))

    score = round(min(attention_component + stability_component + presence_component + blink_component, 100.0), 2)

    indicators: list[str] = []
    if payload.gaze_stability < 0.5:
        indicators.append("low_gaze_stability")
    if payload.face_presence_ratio < 0.7:
        indicators.append("inconsistent_face_presence")
    if payload.attention_seconds < 20:
        indicators.append("short_attention_window")

    if score >= 75:
        risk_band = "low"
    elif score >= 50:
        risk_band = "moderate"
    else:
        risk_band = "high"

    return {
        "user_id": payload.user_id,
        "eye_score": score,
        "risk_band": risk_band,
        "confidence": 0.72,
        "indicators": indicators,
        "summary": "Eye-tracking baseline analysis completed.",
    }
