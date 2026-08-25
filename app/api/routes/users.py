from fastapi import APIRouter

from app.api.deps import CurrentUser
from app.schemas.user import UserPublic

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserPublic)
def get_me(current_user: CurrentUser):
    return current_user
