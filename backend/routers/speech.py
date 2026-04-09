from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from backend.ai_models.speech_analysis import analyze_speech_features
from backend.ai_models.speech_analysis import apply_wav2vec2_adjustment
from backend.ai_models.speech_analysis import AudioFeatureExtractionError
from backend.ai_models.speech_analysis import extract_audio_features
from backend.ai_models.speech_analysis import speech_risk_band_from_score
from backend.ai_models.speech_transcriber import SpeechTranscriptionError
from backend.ai_models.speech_transcriber import transcribe_audio_file
from backend.ai_models.speech_wav2vec2 import Wav2Vec2FeatureError
from backend.ai_models.speech_wav2vec2 import extract_wav2vec2_features
from backend.core.config import get_settings
from backend.dependencies.auth import AuthUser, get_current_user, resolve_user_id
from backend.schemas.speech import SpeechAnalyzeAudioResponse, SpeechAnalyzeRequest, SpeechAnalyzeResponse
from backend.services.assessment_store import update_module_result

router = APIRouter(tags=["speech"])


@router.post("/speech/analyze", response_model=SpeechAnalyzeResponse)
async def analyze_speech(payload: SpeechAnalyzeRequest, auth_user: AuthUser = Depends(get_current_user)) -> SpeechAnalyzeResponse:
    user_id = resolve_user_id(payload.user_id, auth_user)
    payload.user_id = user_id
    result = analyze_speech_features(payload)
    update_module_result(user_id, "speech", result["speech_score"])
    return SpeechAnalyzeResponse(**result)


@router.post("/speech/analyze-audio", response_model=SpeechAnalyzeAudioResponse)
async def analyze_speech_audio(
    audio_file: UploadFile = File(...),
    user_id: str | None = Form(default=None),
    session_id: str | None = Form(default=None),
    use_wav2vec2: bool = Form(default=True),
    auth_user: AuthUser = Depends(get_current_user),
) -> SpeechAnalyzeAudioResponse:
    resolved_user_id = resolve_user_id(user_id, auth_user)

    if audio_file.content_type not in {
        "audio/wav",
        "audio/x-wav",
        "audio/mpeg",
        "audio/mp3",
        "audio/mp4",
        "audio/x-m4a",
        "audio/aac",
        "audio/ogg",
        "application/octet-stream",
    }:
        raise HTTPException(status_code=415, detail="Unsupported audio file format.")

    suffix = Path(audio_file.filename or "recording.wav").suffix or ".wav"
    settings = get_settings()

    with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        temp_path = tmp.name
        file_bytes = await audio_file.read()
        if not file_bytes:
            raise HTTPException(status_code=400, detail="Uploaded audio file is empty.")

        max_audio_bytes = int(settings.speech_max_audio_mb * 1024 * 1024)
        if len(file_bytes) > max_audio_bytes:
            raise HTTPException(
                status_code=413,
                detail=f"Audio file exceeds maximum size of {settings.speech_max_audio_mb} MB.",
            )

        tmp.write(file_bytes)

    try:
        features = extract_audio_features(temp_path)
        transcript_text = transcribe_audio_file(temp_path)
        payload = SpeechAnalyzeRequest(
            user_id=resolved_user_id,
            session_id=session_id,
            audio_duration_seconds=features["audio_duration_seconds"],
            transcript_text=transcript_text,
            voice_variability=features["voice_variability"],
            pause_ratio=features["pause_ratio"],
        )
        result = analyze_speech_features(payload)

        wav2vec2_metrics = None
        wav2vec2_adjustment = None
        if settings.wav2vec2_enabled and use_wav2vec2:
            wav2vec2_metrics = extract_wav2vec2_features(temp_path)
            adjusted_score, wav2vec2_adjustment = apply_wav2vec2_adjustment(result["speech_score"], wav2vec2_metrics)
            result["speech_score"] = adjusted_score
            result["risk_band"] = speech_risk_band_from_score(adjusted_score)
            result["indicators"].append("wav2vec2_enhanced")

        update_module_result(resolved_user_id, "speech", result["speech_score"])

        return SpeechAnalyzeAudioResponse(
            **result,
            transcript_text=transcript_text,
            extracted_metrics=features,
            wav2vec2_metrics=wav2vec2_metrics,
            wav2vec2_adjustment=wav2vec2_adjustment,
        )
    except AudioFeatureExtractionError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except SpeechTranscriptionError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Wav2Vec2FeatureError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    finally:
        Path(temp_path).unlink(missing_ok=True)
