from __future__ import annotations

import numpy as np

import librosa

from backend.core.config import get_settings
from backend.schemas.speech import SpeechAnalyzeRequest


class AudioFeatureExtractionError(RuntimeError):
    pass


def speech_risk_band_from_score(score: float) -> str:
    if score >= 75:
        return "low"
    if score >= 50:
        return "moderate"
    return "high"


def analyze_speech_features(payload: SpeechAnalyzeRequest) -> dict:
    """Starter speech analysis using rule-based feature scoring.

    Replace with pretrained transcription + acoustic feature analysis later.
    """

    settings = get_settings()

    duration_component = (
        min(payload.audio_duration_seconds / max(settings.speech_duration_target_seconds, 1.0), 1.0)
        * settings.speech_duration_weight
    )
    variability_component = (1.0 - payload.voice_variability) * settings.speech_variability_weight
    pause_component = (1.0 - payload.pause_ratio) * settings.speech_pause_weight
    transcript_component = settings.speech_transcript_weight if payload.transcript_text else (settings.speech_transcript_weight / 3.0)

    score = round(min(duration_component + variability_component + pause_component + transcript_component, 100.0), 2)

    indicators: list[str] = []
    if payload.voice_variability < settings.speech_variability_low_threshold:
        indicators.append("reduced_voice_variability")
    if payload.pause_ratio > settings.speech_pause_high_threshold:
        indicators.append("high_pause_ratio")
    if not payload.transcript_text:
        indicators.append("missing_transcript")

    risk_band = speech_risk_band_from_score(score)

    return {
        "user_id": payload.user_id,
        "speech_score": score,
        "risk_band": risk_band,
        "confidence": 0.68,
        "indicators": indicators,
        "summary": "Speech baseline analysis completed.",
    }


def extract_audio_features(audio_path: str) -> dict[str, float]:
    settings = get_settings()

    try:
        signal, sample_rate = librosa.load(audio_path, sr=16000, mono=True)
    except Exception as exc:
        raise AudioFeatureExtractionError("Failed to decode audio for feature extraction.") from exc

    duration_seconds = float(librosa.get_duration(y=signal, sr=sample_rate))

    if duration_seconds < settings.speech_min_audio_seconds:
        raise AudioFeatureExtractionError(
            f"Audio is too short. Minimum duration is {settings.speech_min_audio_seconds} seconds."
        )

    if signal.size == 0:
        return {
            "audio_duration_seconds": 0.0,
            "voice_variability": 0.0,
            "pause_ratio": 1.0,
        }

    frame_length = int(0.025 * sample_rate)
    hop_length = int(0.010 * sample_rate)
    rms = librosa.feature.rms(y=signal, frame_length=frame_length, hop_length=hop_length)[0]

    rms_mean = float(np.mean(rms)) if rms.size else 0.0
    rms_std = float(np.std(rms)) if rms.size else 0.0
    voice_variability = 0.0 if rms_mean <= 1e-8 else float(np.clip(rms_std / (rms_mean + 1e-8), 0.0, 1.0))

    silence_threshold = max(rms_mean * 0.35, 1e-5)
    pause_ratio = float(np.mean(rms < silence_threshold)) if rms.size else 1.0
    pause_ratio = float(np.clip(pause_ratio, 0.0, 1.0))

    return {
        "audio_duration_seconds": round(duration_seconds, 4),
        "voice_variability": round(voice_variability, 4),
        "pause_ratio": round(pause_ratio, 4),
    }


def apply_wav2vec2_adjustment(base_score: float, wav2vec_features: dict[str, float]) -> tuple[float, float]:
    temporal_consistency = float(wav2vec_features.get("wav2vec_temporal_consistency", 0.5))
    adjustment = (temporal_consistency - 0.5) * 10.0
    adjusted_score = float(np.clip(base_score + adjustment, 0.0, 100.0))
    return round(adjusted_score, 2), round(adjustment, 2)
