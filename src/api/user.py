from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_current_user, get_db
from src.models.users import UsersModel
from src.schemas.auth import AccessTokenRes, LoginSchema, RegisterSchema, TokenResponse
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


@router.post("/auth/refresh", response_model=AccessTokenRes)
async def new_refresh(
    db: Annotated[AsyncSession, Depends(get_db)],
    response: Response,
    refresh_token: Annotated[str | None, Cookie()] = None,
):
    return await user_service.new_refresh(db, response, refresh_token)


@router.post(
    "/auth/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(
    db: Annotated[AsyncSession, Depends(get_db)],
    response: Response,
    current_user: Annotated[UsersModel, Depends(get_current_user)],
    refresh_token: Annotated[str | None, Cookie()] = None,
):
    return await user_service.logout(db, response, current_user, refresh_token)
