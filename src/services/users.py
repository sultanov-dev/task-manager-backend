from datetime import datetime, timezone
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, Response, status
from jwt import ExpiredSignatureError, PyJWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_db
from src.models.refresh_token import RefreshTokenModel
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
    token, jti, expire = create_refresh_token(str(new_user.id))

    token_database = RefreshTokenModel(
        user_id=new_user.id, jti=jti, expires_at=expire, revoked_at=None
    )
    db.add(token_database)
    await db.commit()
    await db.refresh(token_database)

    set_refresh_token(refresh_token=token, response=response)

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
    token, jti, expire = create_refresh_token(str(user.id))

    db_refresh_token = RefreshTokenModel(
        user_id=user.id, jti=jti, expires_at=expire, revoked_at=None
    )
    db.add(db_refresh_token)
    await db.commit()
    await db.refresh(db_refresh_token)

    set_refresh_token(refresh_token=token, response=response)

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

    user_id = payload.get("sub")
    jti = payload.get("jti")

    if not user_id or not jti:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token ma'lumotlari yetarli emas",
        )

    jti_result = await db.execute(
        select(RefreshTokenModel)
        .where(
            RefreshTokenModel.jti == payload.get("jti"),
            RefreshTokenModel.user_id == user_id,
        )
        .with_for_update()
    )
    stored_token = jti_result.scalar_one_or_none()

    if not stored_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found or revoked",
        )

    if stored_token.revoked_at is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked",
        )

    now = datetime.now(timezone.utc)
    expires_at = stored_token.expires_at

    if expires_at.tzinfo is not None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    else:
        expires_at = expires_at.astimezone(timezone.utc)

    if expires_at <= now:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token has expired"
        )

    user = await db.get(UsersModel, str(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Foydalanuvchi topilmadi"
        )

    stored_token.revoked_at = now

    access_token = create_access_token(str(user.id))
    token, jti, expire = create_refresh_token(str(user.id))

    new_token = RefreshTokenModel(
        user_id=user.id, jti=jti, expires_at=expire, revoked_at=None
    )
    db.add(new_token)
    await db.commit()
    await db.refresh(new_token)

    set_refresh_token(token, response)

    return AccessTokenRes(access_token=access_token)
