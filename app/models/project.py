from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class Project(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    organization_id = Column(Integer, ForeignKey("organization.id"), nullable=False)

    organization = relationship("Organization", back_populates="projects")
    tasks = relationship("Task", back_populates="project")
    members = relationship(
        "ProjectMember", back_populates="project", cascade="all, delete-orphan"
    )


class ProjectMember(Base):
    __tablename__ = "project_member"
    project_id = Column(Integer, ForeignKey("project.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), primary_key=True)

    project = relationship("Project", back_populates="members")
    user = relationship("User", back_populates="project_memberships")
