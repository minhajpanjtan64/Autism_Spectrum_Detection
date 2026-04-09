from __future__ import annotations

from functools import lru_cache

from faster_whisper import WhisperModel

from backend.core.config import get_settings


class SpeechTranscriptionError(RuntimeError):
    pass


@lru_cache(maxsize=1)
def get_whisper_model() -> WhisperModel:
    settings = get_settings()
    return WhisperModel(
        model_size_or_path=settings.whisper_model_size,
        device=settings.whisper_device,
        compute_type=settings.whisper_compute_type,
    )


def transcribe_audio_file(audio_path: str) -> str:
    try:
        model = get_whisper_model()
        segments, _ = model.transcribe(audio_path, vad_filter=True)
        transcript_parts = [segment.text.strip() for segment in segments if segment.text and segment.text.strip()]
        return " ".join(transcript_parts).strip()
    except Exception as exc:
        raise SpeechTranscriptionError("Whisper transcription failed for the uploaded audio.") from exc


def warmup_whisper_model() -> None:
    _ = get_whisper_model()
