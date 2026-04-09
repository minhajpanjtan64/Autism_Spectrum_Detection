from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.ai_models.speech_transcriber import warmup_whisper_model
from backend.ai_models.speech_wav2vec2 import warmup_wav2vec2_model
from backend.core.config import get_settings
from backend.core.logging import configure_logging
from backend.routers import eye, mcq, report, speech, user

configure_logging()
settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(eye.router)
app.include_router(speech.router)
app.include_router(mcq.router)
app.include_router(report.router)


@app.on_event("startup")
async def startup_event() -> None:
    if settings.speech_model_warmup:
        warmup_whisper_model()
        if settings.wav2vec2_enabled:
            warmup_wav2vec2_model()


@app.get("/health")
async def health_check() -> dict:
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": "0.1.0",
    }
