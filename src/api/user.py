from typing import Annotated

from fastapi import APIRouter, Depends

from src.dependencies import get_current_user
from src.models.auth import UsersModel
from src.schemas.user import UserResponse

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_user(current_user: Annotated[UsersModel, Depends(get_current_user)]):
    return current_user
