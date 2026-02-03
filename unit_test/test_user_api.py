"""Unit tests for User API endpoints."""

import pytest


class TestUserRegistration:
    """Test user registration endpoint."""

    def test_register_success(self, client):
        """Test successful user registration."""
        response = client.post("/api/user/register", json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123",
            "role": "user"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["username"] == "newuser"
        assert data["data"]["email"] == "newuser@skyrisai.com"
        assert "id" in data["data"]

    def test_register_duplicate_username(self, client, test_user):
        """Test registration with duplicate username."""
        response = client.post("/api/user/register", json={
            "username": "testuser",
            "email": "another@example.com",
            "password": "password123",
            "role": "user"
        })
        assert response.status_code == 400

    def test_register_invalid_email(self, client):
        """Test registration with invalid email format."""
        response = client.post("/api/user/register", json={
            "username": "newuser",
            "email": "invalid-email",
            "password": "password123",
            "role": "user"
        })
        assert response.status_code == 422


class TestUserLogin:
    """Test user login endpoint."""

    def test_login_success(self, client, test_user):
        """Test successful login."""
        response = client.post("/api/user/login", json={
            "username": "testuser",
            "password": "testpass"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "access_token" in data["data"]
        assert data["data"]["token_type"] == "bearer"

    def test_login_wrong_password(self, client, test_user):
        """Test login with wrong password."""
        response = client.post("/api/user/login", json={
            "username": "testuser",
            "password": "wrongpass"
        })
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent username."""
        response = client.post("/api/user/login", json={
            "username": "nonexistent",
            "password": "password123"
        })
        assert response.status_code == 401


class TestUserInfo:
    """Test user information endpoints."""

    def test_get_current_user(self, client, auth_headers):
        """Test getting current user info."""
        response = client.get("/api/user/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["username"] == "testuser"

    def test_get_current_user_unauthorized(self, client):
        """Test getting current user without authentication."""
        response = client.get("/api/user/me")
        assert response.status_code == 401

    def test_get_user_by_username(self, client, test_user):
        """Test getting user info by username."""
        response = client.get("/api/user/info/testuser")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["username"] == "testuser"

    def test_get_nonexistent_user(self, client):
        """Test getting non-existent user."""
        response = client.get("/api/user/info/nonexistent")
        assert response.status_code == 404
