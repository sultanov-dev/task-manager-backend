from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, Response, status
from jwt import ExpiredSignatureError, PyJWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_db
from src.models.users import UsersModel
from src.schemas.auth import (
    AccessTokenRes,
    LoginSchema,
    RegisterResponse,
    RegisterSchema,
    TokenResponse,
)
from src.security import (
    create_access_token,
    create_refresh_token,
    decode_jwt,
    hash_password,
    verify_password,
)
from src.utils import set_refresh_token


async def user_register(
    db: Annotated[AsyncSession, Depends(get_db)],
    response: Response,
    data: RegisterSchema,
) -> TokenResponse:
    result = await db.execute(select(UsersModel).where(UsersModel.email == data.email))
    existingUser = result.scalar_one_or_none()

    if existingUser:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Bunaqa email allaqachon mavjud!",
        )

    hashed_password = hash_password(data.password)
    new_user = UsersModel(name=data.name, email=data.email, password=hashed_password)

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    access_token = create_access_token(str(new_user.id))
    refresh_token = create_refresh_token(str(new_user.id))

    set_refresh_token(refresh_token=refresh_token, response=response)

    return TokenResponse(
        access_token=access_token, user=RegisterResponse.model_validate(new_user)
    )


async def user_login(
    db: Annotated[AsyncSession, Depends(get_db)], response: Response, data: LoginSchema
) -> TokenResponse:
    result_login = await db.execute(
        select(UsersModel).where(UsersModel.email == data.email)
    )
    user = result_login.scalar_one_or_none()

    if not user or not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email yoki parol noto'g'ri",
        )

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    set_refresh_token(refresh_token=refresh_token, response=response)

    return TokenResponse(
        access_token=access_token, user=RegisterResponse.model_validate(user)
    )


async def new_refresh(
    db: Annotated[AsyncSession, Depends(get_db)],
    response: Response,
    refresh_token: Annotated[str | None, Cookie()] = None,
) -> AccessTokenRes:
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token topilmadi"
        )

    try:
        payload = decode_jwt(refresh_token)
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token eskirgan, qayta login qilish kerak",
        )
    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token yaroqsiz"
        )

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token turi xato"
        )

    user = await db.get(UsersModel, str(payload["sub"]))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Foydalanuvchi topilmadi"
        )

    access_token = create_access_token(str(user.id))
    new_refresh_token = create_refresh_token(str(user.id))

    set_refresh_token(new_refresh_token, response)

    return AccessTokenRes(access_token=access_token)
