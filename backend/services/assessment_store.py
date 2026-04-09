from __future__ import annotations

from datetime import datetime, timezone
from threading import Lock

MODULES = ("eye", "speech", "mcq", "report")

_store_lock = Lock()
_user_store: dict[str, dict] = {}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _get_or_create_user_record(user_id: str) -> dict:
    record = _user_store.get(user_id)
    if record is None:
        record = {
            "updated_at": _utc_now(),
            "completed_modules": set(),
            "scores": {},
            "report": None,
        }
        _user_store[user_id] = record
    return record


def update_module_result(user_id: str, module: str, score: float | None = None) -> None:
    with _store_lock:
        record = _get_or_create_user_record(user_id)
        if module in MODULES:
            record["completed_modules"].add(module)
        if score is not None:
            record["scores"][f"{module}_score"] = round(float(score), 2)
        record["updated_at"] = _utc_now()


def save_report(user_id: str, report_data: dict, pdf_path: str | None) -> None:
    with _store_lock:
        record = _get_or_create_user_record(user_id)
        record["completed_modules"].add("report")
        record["report"] = {
            "pdf_path": pdf_path,
            "report_json": report_data,
        }
        record["updated_at"] = _utc_now()


def get_latest_scores(user_id: str) -> dict[str, float | None]:
    with _store_lock:
        record = _user_store.get(user_id)
        if not record:
            return {"eye_score": None, "speech_score": None, "mcq_score": None}

        scores = record.get("scores", {})
        return {
            "eye_score": scores.get("eye_score"),
            "speech_score": scores.get("speech_score"),
            "mcq_score": scores.get("mcq_score"),
        }


def get_user_status(user_id: str) -> dict:
    with _store_lock:
        record = _user_store.get(user_id)
        if not record:
            return {
                "user_id": user_id,
                "status": "new",
                "completed_modules": [],
                "pending_modules": ["eye", "speech", "mcq", "report"],
                "progress_percent": 0.0,
                "latest_scores": {},
                "report_ready": False,
                "updated_at": _utc_now(),
            }

        completed_modules = sorted(record["completed_modules"])
        pending_modules = [module for module in MODULES if module not in record["completed_modules"]]
        progress_percent = round((len(completed_modules) / len(MODULES)) * 100.0, 2)

        if len(completed_modules) == 0:
            status = "new"
        elif len(completed_modules) == len(MODULES):
            status = "completed"
        else:
            status = "in_progress"

        return {
            "user_id": user_id,
            "status": status,
            "completed_modules": completed_modules,
            "pending_modules": pending_modules,
            "progress_percent": progress_percent,
            "latest_scores": record.get("scores", {}),
            "report_ready": record.get("report") is not None,
            "updated_at": datetime.fromisoformat(record["updated_at"]),
        }
