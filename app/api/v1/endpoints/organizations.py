from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.models.organization import Organization
from app.models.user import User, UserRole
from app.core.security import get_password_hash
from app.schemas.organization import (
    Organization as OrganizationSchema,
    OrganizationCreate,
)
from app.schemas.user import UserCreate

router = APIRouter()


@router.post("/", response_model=OrganizationSchema)
def create_organization(
    *,
    db: Session = Depends(deps.get_db),
    org_in: OrganizationCreate,
    # In a real app, this might be open or super-admin only.
    # For this assignment, allowing open creation to bootstrap.
) -> Any:
    """
    Create new organization.
    """
    org = db.query(Organization).filter(Organization.name == org_in.name).first()
    if org:
        raise HTTPException(
            status_code=400,
            detail="The organization with this name already exists",
        )
    db_obj = Organization(name=org_in.name)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


from pydantic import BaseModel


class RegisterRequest(BaseModel):
    organization_name: str
    email: str
    password: str
    full_name: str


@router.post("/register", response_model=Any)
def register_organization_and_admin(
    *,
    db: Session = Depends(deps.get_db),
    request: RegisterRequest,
) -> Any:
    """
    Bootstrap endpoint: Create Org and Admin User.
    """
    org = (
        db.query(Organization)
        .filter(Organization.name == request.organization_name)
        .first()
    )
    if org:
        raise HTTPException(status_code=400, detail="Organization exists")

    user = db.query(User).filter(User.email == request.email).first()
    if user:
        raise HTTPException(status_code=400, detail="User email exists")

    new_org = Organization(name=request.organization_name)
    db.add(new_org)
    db.flush()

    new_user = User(
        email=request.email,
        hashed_password=get_password_hash(request.password),
        full_name=request.full_name,
        role=UserRole.ADMIN,
        organization_id=new_org.id,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "Organization and Admin created",
        "organization_id": new_org.id,
        "user_id": new_user.id,
    }
