"""Base utilities for agent tools."""

from typing import Optional

from sqlalchemy.orm import Session

from app.models.user import User


class ToolContext:
    """Thread-local context for database session and current user."""

    db: Optional[Session] = None
    current_user: Optional[User] = None

    @classmethod
    def set_context(cls, db: Session, user: User):
        cls.db = db
        cls.current_user = user

    @classmethod
    def clear_context(cls):
        cls.db = None
        cls.current_user = None
