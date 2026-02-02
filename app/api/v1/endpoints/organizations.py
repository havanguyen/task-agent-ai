
from typing import Any
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.organization import (
    Organization as OrganizationSchema,
    OrganizationCreate,
)
from app.services import organization_service

router = APIRouter()


class RegisterRequest(BaseModel):

    organization_name: str
    email: str
    password: str
    full_name: str


@router.post("/", response_model=OrganizationSchema)
def create_organization(
    *,
    db: Session = Depends(deps.get_db),
    org_in: OrganizationCreate,
) -> Any:
    return organization_service.create_organization(db, org_in)


@router.post("/register", response_model=Any)
def register_organization_and_admin(
    *,
    db: Session = Depends(deps.get_db),
    request: RegisterRequest,
) -> Any:
    return organization_service.register_with_admin(
        db,
        organization_name=request.organization_name,
        email=request.email,
        password=request.password,
        full_name=request.full_name,
    )
