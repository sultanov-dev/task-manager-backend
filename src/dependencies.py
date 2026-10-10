from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import HTTPException, status
from fastapi.params import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import async_session
from src.models.users import UsersModel
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
    except PyJWTError:
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
