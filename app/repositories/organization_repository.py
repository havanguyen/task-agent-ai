from typing import Optional
from sqlalchemy.orm import Session

from app.repositories.base import BaseRepository
from app.models.organization import Organization
from app.schemas.organization import OrganizationCreate


class OrganizationRepository(
    BaseRepository[Organization, OrganizationCreate, OrganizationCreate]
):

    def __init__(self):
        super().__init__(Organization)

    def get_by_name(self, db: Session, name: str) -> Optional[Organization]:
        return db.query(Organization).filter(Organization.name == name).first()

    def name_exists(self, db: Session, name: str) -> bool:
        return self.get_by_name(db, name) is not None

    def create_organization(self, db: Session, *, name: str) -> Organization:
        org = Organization(name=name)
        db.add(org)
        db.flush()
        db.refresh(org)
        return org

organization_repository = OrganizationRepository()
