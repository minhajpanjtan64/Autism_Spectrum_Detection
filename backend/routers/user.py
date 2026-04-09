from fastapi import APIRouter, Depends

from backend.dependencies.auth import AuthUser, get_current_user
from backend.schemas.user import UserStatusResponse
from backend.services.assessment_store import get_user_status as get_user_status_snapshot

router = APIRouter(tags=["user"])


@router.get("/user/status", response_model=UserStatusResponse)
async def get_user_status(auth_user: AuthUser = Depends(get_current_user)) -> UserStatusResponse:
    status = get_user_status_snapshot(auth_user.uid)
    return UserStatusResponse(**status)
