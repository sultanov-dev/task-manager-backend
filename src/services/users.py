from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_db
from src.models.users import UsersModel
from src.schemas.auth import RegisterSchema
from src.security import hash_password


async def user_register(
    db: Annotated[AsyncSession, Depends(get_db)], data: RegisterSchema
):
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

    return new_user
