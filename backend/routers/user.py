from fastapi import APIRouter

from backend.schemas.user import UserStatusResponse

router = APIRouter(tags=["user"])


@router.get("/user/status", response_model=UserStatusResponse)
async def get_user_status(user_id: str | None = None) -> UserStatusResponse:
    return UserStatusResponse(
        user_id=user_id,
        status="active",
        completed_modules=["authentication"],
        pending_modules=["eye", "speech", "mcq", "report"],
    )
