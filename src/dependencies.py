from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import HTTPException, status
from fastapi.params import Cookie, Depends, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import ExpiredSignatureError, PyJWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import async_session
from src.models.auth import UsersModel
from src.models.enums import Priority, TaskStatus
from src.schemas.tasks import TaskFilters
from src.security import decode_jwt


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


bearer_schema = HTTPBearer()


async def get_current_user(
    credintials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_schema)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UsersModel:
    token = credintials.credentials

    try:
        payload = decode_jwt(token)
    except (PyJWTError, ExpiredSignatureError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token yaroqsiz yoki muddati tugagan",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token talab qilinadi",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User topilmadi",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(select(UsersModel).where(UsersModel.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User topilmadi",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_refresh_token(
    refresh_token: Annotated[str | None, Cookie()] = None,
) -> str:
    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found",
        )

    return refresh_token


def get_filters(
    status: Annotated[TaskStatus | None, Query(alias="status")] = None,
    priority: Annotated[Priority | None, Query(alias="priority")] = None,
    page: Annotated[int, Query(alias="page", ge=1)] = 1,
    limit: Annotated[int, Query(alias="limit", ge=10, le=50)] = 10,
) -> TaskFilters:
    return TaskFilters(status=status, priority=priority, page=page, limit=limit)
