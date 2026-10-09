from fastapi import Response


def set_refresh_token(refresh_token: str, response: Response):
    return response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        path="/auth",
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
    )
