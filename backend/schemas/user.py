from datetime import datetime, timezone

from pydantic import BaseModel, Field


class UserStatusResponse(BaseModel):
    user_id: str | None = None
    status: str = Field(default="active")
    completed_modules: list[str] = Field(default_factory=list)
    pending_modules: list[str] = Field(default_factory=list)
    progress_percent: float = 0.0
    latest_scores: dict[str, float] = Field(default_factory=dict)
    report_ready: bool = False
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
