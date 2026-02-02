import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base_class import Base
from app.api.deps import get_db


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


Base.metadata.create_all(bind=engine)

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


class TestAuth:

    def test_register_organization(self):
        response = client.post(
            "/api/v1/organizations/register",
            json={
                "organization_name": "Test Organization",
                "email": "admin@testorg.com",
                "password": "testpassword123",
                "full_name": "Test Admin",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "organization_id" in data["data"]
        assert "user_id" in data["data"]

    def test_login_success(self):
        client.post(
            "/api/v1/organizations/register",
            json={
                "organization_name": "Login Test Org",
                "email": "logintest@example.com",
                "password": "password123",
                "full_name": "Login User",
            },
        )

        response = client.post(
            "/api/v1/auth/login",
            json={"email": "logintest@example.com", "password": "password123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]
        assert data["data"]["token_type"] == "bearer"

        assert "ACCESS_TOKEN" in response.cookies
        assert "REFRESH_TOKEN" in response.cookies

    def test_login_wrong_password(self):
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "admin@testorg.com", "password": "wrongpassword"},
        )
        assert response.status_code == 400

    def test_get_current_user(self):
        client.post(
            "/api/v1/organizations/register",
            json={
                "organization_name": "Me Test Org",
                "email": "metest@example.com",
                "password": "password123",
                "full_name": "Me User",
            },
        )

        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "metest@example.com", "password": "password123"},
        )
        token = login_response.json()["data"]["access_token"]

        response = client.get(
            "/api/v1/users/me", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["email"] == "metest@example.com"
        assert data["data"]["full_name"] == "Me User"

    def test_logout(self):
        response = client.post("/api/v1/auth/logout")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Logged out successfully"


class TestHealthCheck:

    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "ok"
