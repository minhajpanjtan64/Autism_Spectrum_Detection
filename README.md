# AI-Based Autism Screening & Early Detection System

Production-oriented backend scaffold for a research-focused autism screening application.

## Project Scope
- Research screening support only
- Not a medical diagnosis tool
- React Native frontend, FastAPI backend
- Modular AI pipeline for eye, speech, and MCQ-based scoring

## Current Status
- Backend scaffold initialized
- First live endpoint available
- API structure ready for frontend integration

## Repository Structure
- `backend/` — FastAPI application
- `backend/routers/` — API route handlers
- `backend/ai_models/` — scoring and analysis logic
- `backend/services/` — report generation and helpers
- `backend/schemas/` — request and response models
- `backend/core/` — configuration and logging

## Setup
1. Create and activate a Python virtual environment.
2. Install dependencies from `requirements.txt`.
3. Copy `.env.example` to `.env` and update values if needed.
4. Run the backend with Uvicorn.

## Local Run
From the project root:
- `uvicorn backend.main:app --reload`

## Quick API Checks
- Health: `GET http://127.0.0.1:8000/health`
- Swagger docs: `http://127.0.0.1:8000/docs`

Example flow (PowerShell):
- `Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/eye/analyze -Headers @{ Authorization = "Bearer <ID_TOKEN>" } -ContentType "application/json" -Body '{"attention_seconds":35,"gaze_stability":0.72,"face_presence_ratio":0.9,"blink_rate_per_minute":18}'`
- `Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/speech/analyze -Headers @{ Authorization = "Bearer <ID_TOKEN>" } -ContentType "application/json" -Body '{"audio_duration_seconds":40,"transcript_text":"sample","voice_variability":0.45,"pause_ratio":0.3}'`
- `Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/mcq/submit -Headers @{ Authorization = "Bearer <ID_TOKEN>" } -ContentType "application/json" -Body '{"answers":[{"question_id":"q1","answer_value":2},{"question_id":"q2","answer_value":3}]}'`
- `Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/generate-report -Headers @{ Authorization = "Bearer <ID_TOKEN>" } -ContentType "application/json" -Body '{"use_saved_scores":true,"save_pdf":false}'`
- `Invoke-RestMethod -Method Get -Uri 'http://127.0.0.1:8000/user/status' -Headers @{ Authorization = "Bearer <ID_TOKEN>" }`

## API Endpoints
- `GET /health`
- `GET /user/status`
- `POST /eye/analyze`
- `POST /speech/analyze`
- `POST /speech/analyze-audio`
- `POST /mcq/submit`
- `POST /generate-report`

## Frontend Integration
Point the React Native app to the backend base URL in Axios.

## Firebase Auth Integration (Backend)
- All screening APIs require `Authorization: Bearer <Firebase ID Token>`.
- Backend verifies token via Firebase Admin SDK and uses verified `uid` as user identity.
- Configure `.env`:
	- `FIREBASE_AUTH_REQUIRED=true`
	- `FIREBASE_CREDENTIALS_PATH=/absolute/path/to/firebase-service-account.json`
- Frontend Axios should attach the ID token for every protected API request.

Speech model configuration:
- Whisper: `WHISPER_MODEL_SIZE`, `WHISPER_DEVICE`, `WHISPER_COMPUTE_TYPE`
- Wav2Vec2: `WAV2VEC2_MODEL_NAME`, `WAV2VEC2_ENABLED`
- Runtime tuning: `SPEECH_MODEL_WARMUP`, `SPEECH_MIN_AUDIO_SECONDS`, `SPEECH_MAX_AUDIO_MB`
- Calibration knobs: `SPEECH_DURATION_TARGET_SECONDS`, `SPEECH_DURATION_WEIGHT`, `SPEECH_VARIABILITY_WEIGHT`, `SPEECH_PAUSE_WEIGHT`, `SPEECH_TRANSCRIPT_WEIGHT`

Audio upload example (PowerShell):
- `Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/speech/analyze-audio -Headers @{ Authorization = "Bearer <ID_TOKEN>" } -Form @{ audio_file = Get-Item "C:\path\sample.wav" }`

## Development Notes
- Start with mocked analysis scores.
- Add pretrained model integration later.
- Keep question text compliant with licensing rules.

## Git Workflow
- Commit after each milestone.
- Push often to keep a safe version history.
- Keep frontend and backend in separate folders or repositories if that is easier for your team.
