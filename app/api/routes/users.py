from fastapi import APIRouter

from app.api.deps import CurrentUser, UserServiceDep
from app.application.user.dto import UserResponseDTO

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponseDTO)
def get_me(current_user: CurrentUser):
    return UserResponseDTO.from_domain(current_user)
