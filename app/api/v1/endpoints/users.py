from typing import Any, List
from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.api import deps
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.organization import Organization
from app.schemas.user import User as UserSchema, UserCreate, UserUpdate

router = APIRouter()


@router.get("/", response_model=List[UserSchema])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Retrieve users. Only for Admins.
    Filter by current user's organization.
    """
    users = (
        db.query(User)
        .filter(User.organization_id == current_user.organization_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return users


@router.post("/", response_model=UserSchema)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Create new user. Only Admin can create users for their organization.
    """
    if user_in.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=400, detail="Cannot create user for another organization"
        )

    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system",
        )

    obj_in_data = jsonable_encoder(user_in)
    del obj_in_data["password"]
    db_obj = User(**obj_in_data, hashed_password=get_password_hash(user_in.password))
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


@router.get("/me", response_model=UserSchema)
def read_user_me(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user
