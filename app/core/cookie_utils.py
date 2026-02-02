from fastapi import Response

ACCESS_TOKEN_MAX_AGE = 10 * 60
REFRESH_TOKEN_MAX_AGE = 7 * 24 * 60 * 60


def set_access_cookie(response: Response, access_token: str) -> None:
    response.set_cookie(
        key="ACCESS_TOKEN",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        path="/",
        max_age=ACCESS_TOKEN_MAX_AGE,
    )


def set_refresh_cookie(response: Response, refresh_token: str) -> None:
    if refresh_token is None:
        return
    response.set_cookie(
        key="REFRESH_TOKEN",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        path="/",
        max_age=REFRESH_TOKEN_MAX_AGE,
    )


def clear_cookies(response: Response) -> None:
    response.delete_cookie(key="ACCESS_TOKEN", path="/")
    response.delete_cookie(key="REFRESH_TOKEN", path="/")


def set_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    set_access_cookie(response, access_token)
    set_refresh_cookie(response, refresh_token)
