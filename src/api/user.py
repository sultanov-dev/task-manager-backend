from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_db
from src.schemas.auth import LoginSchema, RegisterSchema, TokenResponse
from src.services import users as user_service

router = APIRouter()


@router.post(
    "/auth/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED
)
async def user_register(
    db: Annotated[AsyncSession, Depends(get_db)],
    response: Response,
    payload: RegisterSchema,
):
    return await user_service.user_register(db, response, payload)


@router.post(
    "/auth/login", response_model=TokenResponse, status_code=status.HTTP_200_OK
)
async def user_login(
    db: Annotated[AsyncSession, Depends(get_db)],
    response: Response,
    payload: LoginSchema,
):
    return await user_service.user_login(db, response, payload)
