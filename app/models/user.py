import enum
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    MEMBER = "member"


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, index=True)
    is_active = Column(Boolean(), default=True)
    role = Column(Enum(UserRole), default=UserRole.MEMBER, nullable=False)

    organization_id = Column(Integer, ForeignKey("organization.id"), nullable=True)
    organization = relationship("Organization", back_populates="users")

    # Projects user is a member of (Many-to-Many maybe? Or just direct assignment to tasks?)
    # Requirements: "Project... Can add/remove members." so likely M2M.
    # But for now, let's keep it simple. If projects belong to org, and user belongs to org...
    # "Projects... Can add/remove members." -> implies subset of org members.

    tasks_assigned = relationship("Task", back_populates="assignee")
    comments = relationship("Comment", back_populates="author")
    notifications = relationship("Notification", back_populates="user")

    # Many-to-Many for project membership
    project_memberships = relationship("ProjectMember", back_populates="user")
