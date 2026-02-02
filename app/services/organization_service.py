

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.organization import Organization
from app.models.user import User, UserRole
from app.core.security import get_password_hash
from app.repositories import organization_repository, user_repository
from app.schemas.organization import OrganizationCreate


class OrganizationService:

    def create_organization(
        self, db: Session, org_in: OrganizationCreate
    ) -> Organization:
        if organization_repository.name_exists(db, org_in.name):
            raise HTTPException(
                status_code=400, detail="The organization with this name already exists"
            )

        org = organization_repository.create_organization(db, name=org_in.name)
        db.commit()
        db.refresh(org)

        return org

    def register_with_admin(
        self,
        db: Session,
        organization_name: str,
        email: str,
        password: str,
        full_name: str,
    ) -> dict:
        if organization_repository.name_exists(db, organization_name):
            raise HTTPException(status_code=400, detail="Organization exists")

        if user_repository.email_exists(db, email):
            raise HTTPException(status_code=400, detail="User email exists")

        new_org = organization_repository.create_organization(
            db, name=organization_name
        )

        new_user = user_repository.create_user(
            db,
            email=email,
            hashed_password=get_password_hash(password),
            full_name=full_name,
            role=UserRole.ADMIN,
            organization_id=new_org.id,
        )

        db.commit()
        db.refresh(new_user)

        return {
            "message": "Organization and Admin created",
            "organization_id": new_org.id,
            "user_id": new_user.id,
        }

organization_service = OrganizationService()
