from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api import deps
from app.models.user import User
from app.schemas.user import User as UserSchema, UserCreate
from app.schemas.api_response import ApiResponse
from app.services import user_service

router = APIRouter()


@router.get("/")
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_admin),
):
    users = user_service.list_users(db, current_user, skip=skip, limit=limit)
    return ApiResponse.success_response(
        data=users, message="Users retrieved successfully"
    )


@router.post("/")
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
    current_user: User = Depends(deps.get_current_active_admin),
):
    user = user_service.create_user(db, current_user, user_in)
    return ApiResponse.success_response(
        data=user, message="User created successfully", status_code=201
    )


@router.get("/me")
def read_user_me(
    current_user: User = Depends(deps.get_current_active_user),
):
    user = user_service.get_current_user(current_user)
    return ApiResponse.success_response(
        data=user, message="User retrieved successfully"
    )
