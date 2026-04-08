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

## API Endpoints
- `GET /health`
- `GET /user/status`
- `POST /eye/analyze`
- `POST /speech/analyze`
- `POST /mcq/submit`
- `POST /generate-report`

## Frontend Integration
Point the React Native app to the backend base URL in Axios.

## Development Notes
- Start with mocked analysis scores.
- Add pretrained model integration later.
- Keep question text compliant with licensing rules.

## Git Workflow
- Commit after each milestone.
- Push often to keep a safe version history.
- Keep frontend and backend in separate folders or repositories if that is easier for your team.
