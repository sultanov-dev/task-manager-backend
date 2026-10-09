from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class RegisterSchema(BaseModel):
    name: str = Field(..., min_length=4, max_length=24)
    email: EmailStr
    password: str = Field(..., min_length=6)

    @field_validator("password")
    @classmethod
    def check_password(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Parol kamida 8 belgidan iborat bo'lishi kerak")
        return v


class LoginSchema(BaseModel):
    email: EmailStr
    password: str


class RegisterResponse(BaseModel):
    id: UUID
    name: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: RegisterResponse


class AccessTokenRes(BaseModel):
    access_token: str
    token_type: str = "bearer"
