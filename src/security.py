import uuid
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from src.core.config import settings

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

password_hash_fn = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash_fn.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return password_hash_fn.verify(plain, hashed)


def create_access_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": user_id, "type": "access", "exp": expire}

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(user_id: str):
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    jti = str(uuid.uuid4())
    payload = {
        "sub": user_id,
        "jti": jti,
        "type": "refresh",
        "exp": expire,
    }

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)

    return token, jti, expire


def decode_jwt(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
