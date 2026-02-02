
from typing import List
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.models.user import User
from app.core.security import get_password_hash
from app.repositories import user_repository
from app.schemas.user import UserCreate


class UserService:

    def list_users(
        self, db: Session, current_user: User, *, skip: int = 0, limit: int = 100
    ) -> List[User]:
        return user_repository.get_by_organization(
            db, current_user.organization_id, skip=skip, limit=limit
        )

    def create_user(self, db: Session, current_user: User, user_in: UserCreate) -> User:
        if user_in.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=400, detail="Cannot create user for another organization"
            )

        if user_repository.email_exists(db, user_in.email):
            raise HTTPException(
                status_code=400,
                detail="The user with this username already exists in the system",
            )

        obj_in_data = jsonable_encoder(user_in)
        del obj_in_data["password"]

        user = User(**obj_in_data, hashed_password=get_password_hash(user_in.password))
        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    def get_current_user(self, user: User) -> User:
        return user


user_service = UserService()
