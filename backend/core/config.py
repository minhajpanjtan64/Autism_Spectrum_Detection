from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    app_name: str = Field(default="AI-Based Autism Screening & Early Detection System")
    debug: bool = Field(default=True)
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    cors_allow_origins: List[str] = Field(default_factory=lambda: ["*"])
    firebase_project_id: str | None = Field(default=None)
    firebase_credentials_path: str | None = Field(default=None)
    firebase_auth_required: bool = Field(default=True)
    whisper_model_size: str = Field(default="small")
    whisper_device: str = Field(default="cpu")
    whisper_compute_type: str = Field(default="int8")
    wav2vec2_model_name: str = Field(default="facebook/wav2vec2-base-960h")
    wav2vec2_enabled: bool = Field(default=True)
    speech_model_warmup: bool = Field(default=False)
    speech_min_audio_seconds: float = Field(default=1.0)
    speech_max_audio_mb: float = Field(default=20.0)
    speech_duration_target_seconds: float = Field(default=60.0)
    speech_duration_weight: float = Field(default=25.0)
    speech_variability_weight: float = Field(default=35.0)
    speech_pause_weight: float = Field(default=25.0)
    speech_transcript_weight: float = Field(default=15.0)
    speech_variability_low_threshold: float = Field(default=0.4)
    speech_pause_high_threshold: float = Field(default=0.6)
    database_url: str | None = Field(default=None)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
