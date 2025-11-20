"""User API test cases.

Tests registration, login, and user info retrieval endpoints using FastAPI TestClient.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_and_login():
    """Test user registration, login, and info retrieval.

    Asserts successful registration, login, and access to user info endpoint.
    """
    # register
    response = client.post("/api/user/register", json={
        "username": "testuser",
        "password": "testpass",
        "email": "test@example.com"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"

    # login
    response = client.post("/api/user/login", json={
        "username": "testuser",
        "password": "testpass"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    assert token

    # get user info
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/user/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"