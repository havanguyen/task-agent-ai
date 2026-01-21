"""
Tests for Core Modules (config, logging, exceptions, security)
"""

import pytest
from datetime import timedelta


class TestConfig:
    """Test configuration module"""

    def test_config_loads(self):
        """Test that settings can be loaded"""
        from app.config import settings

        assert settings is not None
        assert settings.PROJECT_NAME == "River Flow Task Management"

    def test_database_uri_generated(self):
        """Test database URI is generated"""
        from app.config import settings

        assert "postgresql://" in settings.SQLALCHEMY_DATABASE_URI

    def test_redis_uri_generated(self):
        """Test Redis URI is generated"""
        from app.config import settings

        assert "redis://" in settings.REDIS_URI

    def test_api_v1_str(self):
        """Test API version string"""
        from app.config import settings

        assert settings.API_V1_STR == "/api/v1"


class TestSecurity:
    """Test security module"""

    def test_password_hashing(self):
        """Test password hashing and verification"""
        from app.core.security import get_password_hash, verify_password

        password = "testpassword123"
        hashed = get_password_hash(password)

        assert hashed != password
        assert verify_password(password, hashed)
        assert not verify_password("wrongpassword", hashed)

    def test_create_access_token(self):
        """Test JWT token creation"""
        from app.core.security import create_access_token

        token = create_access_token(subject="user123")
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_with_expiry(self):
        """Test JWT token creation with custom expiry"""
        from app.core.security import create_access_token

        token = create_access_token(subject="user123", expires_delta=timedelta(hours=1))
        assert token is not None


class TestLogging:
    """Test logging module"""

    def test_setup_logging(self):
        """Test logging setup"""
        from app.core.logging import setup_logging, logger

        root_logger = setup_logging()
        assert root_logger is not None

    def test_logger_exists(self):
        """Test app logger exists"""
        from app.core.logging import logger

        assert logger is not None
        assert logger.name == "app"


class TestExceptions:
    """Test exception handlers module"""

    def test_api_response_model(self):
        """Test ApiResponse model"""
        from app.core.exceptions import ApiResponse

        response = ApiResponse(
            success=True, message="Test message", data={"key": "value"}
        )
        assert response.success is True
        assert response.message == "Test message"
        assert response.data == {"key": "value"}

    def test_create_response_function(self):
        """Test create_response function"""
        from app.core.exceptions import create_response

        response = create_response(
            success=True, message="OK", data={"test": 123}, status_code=200
        )
        assert response.status_code == 200


class TestModels:
    """Test database models"""

    def test_user_role_enum(self):
        """Test UserRole enum"""
        from app.models.user import UserRole

        assert UserRole.ADMIN.value == "admin"
        assert UserRole.MANAGER.value == "manager"
        assert UserRole.MEMBER.value == "member"

    def test_task_status_enum(self):
        """Test TaskStatus enum"""
        from app.models.task import TaskStatus

        assert TaskStatus.TODO.value == "todo"
        assert TaskStatus.IN_PROGRESS.value == "in-progress"
        assert TaskStatus.DONE.value == "done"

    def test_task_priority_enum(self):
        """Test TaskPriority enum"""
        from app.models.task import TaskPriority

        assert TaskPriority.LOW.value == "low"
        assert TaskPriority.MEDIUM.value == "medium"
        assert TaskPriority.HIGH.value == "high"
