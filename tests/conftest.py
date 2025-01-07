# tests/conftest.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from app.utils import hash_password, create_api_key
from app.models import User




# Configure a test database
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency override for testing
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create tables for the test database
@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# Test client instance
@pytest.fixture(scope="module")
def client():
    return TestClient(app)

# Prepopulate test data
@pytest.fixture(scope="module")
def test_user():
    db = TestingSessionLocal()
    hashed_password = hash_password("testpassword")
    api_key = create_api_key(data={"sub": "testuser"})
    user = User(username="testuser", email="testuser@example.com", hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user