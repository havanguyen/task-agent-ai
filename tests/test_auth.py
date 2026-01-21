"""
Authentication and User Tests
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base_class import Base
from app.api.deps import get_db


# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Create tables
Base.metadata.create_all(bind=engine)

# Override dependency
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


class TestAuth:
    """Test authentication endpoints"""

    def test_register_organization(self):
        """Test organization and admin user registration"""
        response = client.post(
            "/api/v1/organizations/register",
            params={
                "org_name": "Test Organization",
                "email": "admin@testorg.com",
                "password": "testpassword123",
                "full_name": "Test Admin",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "organization_id" in data
        assert "user_id" in data
        assert data["message"] == "Organization and Admin created"

    def test_login_success(self):
        """Test successful login"""
        # First register
        client.post(
            "/api/v1/organizations/register",
            params={
                "org_name": "Login Test Org",
                "email": "logintest@example.com",
                "password": "password123",
                "full_name": "Login User",
            },
        )

        # Then login
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "logintest@example.com", "password": "password123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self):
        """Test login with wrong password"""
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "admin@testorg.com", "password": "wrongpassword"},
        )
        assert response.status_code == 400

    def test_get_current_user(self):
        """Test getting current user info"""
        # Register and login
        client.post(
            "/api/v1/organizations/register",
            params={
                "org_name": "Me Test Org",
                "email": "metest@example.com",
                "password": "password123",
                "full_name": "Me User",
            },
        )

        login_response = client.post(
            "/api/v1/auth/login",
            data={"username": "metest@example.com", "password": "password123"},
        )
        token = login_response.json()["access_token"]

        # Get current user
        response = client.get(
            "/api/v1/users/me", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "metest@example.com"
        assert data["full_name"] == "Me User"


class TestHealthCheck:
    """Test health check endpoint"""

    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
