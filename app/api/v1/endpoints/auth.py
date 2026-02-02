from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api import deps
from app.core import security
from app.core.cookie_utils import clear_cookies, set_cookies
from app.models.user import User
from app.schemas.api_response import ApiResponse
from app.schemas.token import LoginRequest, TokenData

router = APIRouter()


@router.post("/login")
def login_access_token(
    response: Response,
    login_data: LoginRequest,
    db: Session = Depends(deps.get_db),
):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not security.verify_password(
        login_data.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token = security.create_access_token(user.id)
    refresh_token = security.create_refresh_token(user.id)

    set_cookies(response, access_token, refresh_token)

    token_data = TokenData(
        access_token=access_token,
        refresh_token=refresh_token,
    )
    return ApiResponse.success_response(data=token_data, message="Login successful")


@router.post("/refresh")
def refresh_access_token(
    response: Response,
    db: Session = Depends(deps.get_db),
    refresh_token: str = Cookie(None, alias="REFRESH_TOKEN"),
):
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found",
        )

    payload = security.verify_token(refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    new_access_token = security.create_access_token(user.id)
    new_refresh_token = security.create_refresh_token(user.id)

    set_cookies(response, new_access_token, new_refresh_token)

    token_data = TokenData(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
    )
    return ApiResponse.success_response(
        data=token_data, message="Token refreshed successfully"
    )


@router.post("/logout")
def logout(response: Response):
    clear_cookies(response)
    return ApiResponse.success_response(data=None, message="Logged out successfully")
