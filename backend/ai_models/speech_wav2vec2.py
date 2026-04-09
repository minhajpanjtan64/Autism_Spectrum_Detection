from __future__ import annotations

from functools import lru_cache

import numpy as np
import torch
import torchaudio
from transformers import AutoModel, AutoProcessor

from backend.core.config import get_settings


class Wav2Vec2FeatureError(RuntimeError):
    pass


@lru_cache(maxsize=1)
def _get_wav2vec2_processor() -> AutoProcessor:
    settings = get_settings()
    return AutoProcessor.from_pretrained(settings.wav2vec2_model_name)


@lru_cache(maxsize=1)
def _get_wav2vec2_model() -> AutoModel:
    settings = get_settings()
    model = AutoModel.from_pretrained(settings.wav2vec2_model_name)
    model.eval()
    return model


def _load_as_mono_16k(audio_path: str) -> tuple[torch.Tensor, int]:
    waveform, sample_rate = torchaudio.load(audio_path)

    if waveform.ndim == 2 and waveform.shape[0] > 1:
        waveform = waveform.mean(dim=0, keepdim=True)

    if sample_rate != 16000:
        waveform = torchaudio.functional.resample(waveform, orig_freq=sample_rate, new_freq=16000)
        sample_rate = 16000

    return waveform.squeeze(0), sample_rate


def extract_wav2vec2_features(audio_path: str) -> dict[str, float]:
    try:
        waveform, sample_rate = _load_as_mono_16k(audio_path)
        processor = _get_wav2vec2_processor()
        model = _get_wav2vec2_model()

        inputs = processor(waveform.numpy(), sampling_rate=sample_rate, return_tensors="pt")

        with torch.no_grad():
            outputs = model(**inputs)

        hidden = outputs.last_hidden_state.squeeze(0)
        hidden_np = hidden.detach().cpu().numpy()

        frame_energy = np.linalg.norm(hidden_np, axis=1)

        embedding_mean_abs = float(np.mean(np.abs(hidden_np)))
        embedding_std = float(np.std(hidden_np))
        temporal_energy_std = float(np.std(frame_energy)) if frame_energy.size else 0.0
        temporal_consistency = float(np.clip(1.0 - temporal_energy_std, 0.0, 1.0))

        return {
            "wav2vec_embedding_mean_abs": round(embedding_mean_abs, 6),
            "wav2vec_embedding_std": round(embedding_std, 6),
            "wav2vec_temporal_energy_std": round(temporal_energy_std, 6),
            "wav2vec_temporal_consistency": round(temporal_consistency, 6),
        }
    except Exception as exc:
        raise Wav2Vec2FeatureError("Wav2Vec2 feature extraction failed for the uploaded audio.") from exc


def warmup_wav2vec2_model() -> None:
    _ = _get_wav2vec2_processor()
    _ = _get_wav2vec2_model()
