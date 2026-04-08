from datetime import datetime, timezone

from pydantic import BaseModel, Field


class UserStatusResponse(BaseModel):
    user_id: str | None = None
    status: str = Field(default="active")
    completed_modules: list[str] = Field(default_factory=list)
    pending_modules: list[str] = Field(default_factory=list)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
