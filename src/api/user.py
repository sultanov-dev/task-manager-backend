from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_db
from src.schemas.auth import RegisterResponse, RegisterSchema
from src.services import users as user_service

router = APIRouter()


@router.post("/auth/register", response_model=RegisterResponse)
async def user_register(
    db: Annotated[AsyncSession, Depends(get_db)], payload: RegisterSchema
):
    return await user_service.user_register(db, payload)
