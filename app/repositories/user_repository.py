from typing import Any, List, Optional
from sqlalchemy.orm import Session

from app.repositories.base import BaseRepository
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):

    def __init__(self):
        super().__init__(User)

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def get_by_organization(
        self, db: Session, organization_id: int, *, skip: int = 0, limit: int = 100
    ) -> List[User]:
        return (
            db.query(User)
            .filter(User.organization_id == organization_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_user(
        self,
        db: Session,
        *,
        email: str,
        hashed_password: str,
        full_name: str,
        role: Any,
        organization_id: int,
        is_active: bool = True
    ) -> User:
        user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            role=role,
            organization_id=organization_id,
            is_active=is_active,
        )
        db.add(user)
        db.flush()
        db.refresh(user)
        return user

    def email_exists(self, db: Session, email: str) -> bool:
        return self.get_by_email(db, email) is not None

user_repository = UserRepository()
