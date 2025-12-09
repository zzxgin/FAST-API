"""Pytest configuration and fixtures for unit tests."""

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.models import Base
from app.core.database import get_db
from app.models.user import User, UserRole
from passlib.context import CryptContext

# Password context for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Enable foreign key constraints for SQLite
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Enable foreign key constraints in SQLite."""
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database session override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Create a test user in the database."""
    user = User(
        username="testuser",
        email="testuser@example.com",
        password_hash=pwd_context.hash("testpass"),
        role=UserRole.user
        
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_admin(db_session):
    """Create a test admin user in the database."""
    admin = User(
        username="admin",
        email="admin@example.com",
        password_hash=pwd_context.hash("adminpass"),
        role=UserRole.admin
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


@pytest.fixture
def test_publisher(db_session):
    """Create a test publisher user in the database."""
    publisher = User(
        username="publisher",
        email="publisher@example.com",
        password_hash=pwd_context.hash("pubpass"),
        role=UserRole.publisher
    )
    db_session.add(publisher)
    db_session.commit()
    db_session.refresh(publisher)
    return publisher


@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers for test user."""
    response = client.post("/api/user/login", json={
        "username": "testuser",
        "password": "testpass"
    })
    token = response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(client, test_admin):
    """Get authentication headers for admin user."""
    response = client.post("/api/user/login", json={
        "username": "admin",
        "password": "adminpass"
    })
    token = response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def publisher_headers(client, test_publisher):
    """Get authentication headers for publisher user."""
    response = client.post("/api/user/login", json={
        "username": "publisher",
        "password": "pubpass"
    })
    token = response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}
