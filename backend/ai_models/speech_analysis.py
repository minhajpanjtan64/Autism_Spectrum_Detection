from __future__ import annotations

from backend.schemas.speech import SpeechAnalyzeRequest


def analyze_speech_features(payload: SpeechAnalyzeRequest) -> dict:
    """Starter speech analysis using rule-based feature scoring.

    Replace with pretrained transcription + acoustic feature analysis later.
    """

    duration_component = min(payload.audio_duration_seconds / 60.0, 1.0) * 25.0
    variability_component = (1.0 - payload.voice_variability) * 35.0
    pause_component = (1.0 - payload.pause_ratio) * 25.0
    transcript_component = 15.0 if payload.transcript_text else 5.0

    score = round(min(duration_component + variability_component + pause_component + transcript_component, 100.0), 2)

    indicators: list[str] = []
    if payload.voice_variability < 0.4:
        indicators.append("reduced_voice_variability")
    if payload.pause_ratio > 0.6:
        indicators.append("high_pause_ratio")
    if not payload.transcript_text:
        indicators.append("missing_transcript")

    if score >= 75:
        risk_band = "low"
    elif score >= 50:
        risk_band = "moderate"
    else:
        risk_band = "high"

    return {
        "user_id": payload.user_id,
        "speech_score": score,
        "risk_band": risk_band,
        "confidence": 0.68,
        "indicators": indicators,
        "summary": "Speech baseline analysis completed.",
    }
