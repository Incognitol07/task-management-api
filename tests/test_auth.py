# tests/test_auth.py
from app.utils import create_api_key
from app.models import User


# Test cases
def test_register_user(client):
    response = client.post(
        "/auth/register",
        json={
            "username": "newuser", 
            "email": "newuser@example.com", 
            "password": "newpassword"
        },
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Registered successfully"
    assert response.json()["username"] == "newuser"
    assert response.json()["email"] == "newuser@example.com"

def test_register_existing_user(client, test_user: User):
    response = client.post(
        "/auth/register",
        json={
            "username": test_user.username, 
            "email": "another@example.com", 
            "password": "password"
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already registered"

def test_login_user(client, test_user: User):
    response = client.post(
        "/auth/user/login",
        json={
            "email": test_user.email, 
            "password": "testpassword"
        },
    )
    assert response.status_code == 200
    assert "api_key" in response.json()


def test_login_invalid_credentials(client):
    response = client.post(
        "/auth/user/login",
        json={
            "email": "nonexistent@example.com", 
            "password": "wrongpassword"
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid credentials"

def test_protected_route(client, test_user: User):
    # Login to get an access token
    login_response = client.post(
        "/auth/user/login",
        json={
            "email": test_user.email, 
            "password": "testpassword"
        },
    )
    api_key = login_response.json()["api_key"]

    # Use the access token to access a protected route
    response = client.get(
        "/auth/protected-route",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    assert response.status_code == 200
    assert response.json()["detail"].startswith("Hello, testuser!")

def test_register_user_invalid_data(client):
    response = client.post(
        "/auth/register",
        json={
            "username": "", 
            "email": "not-an-email", 
            "password": "short"
        },
    )
    assert "@-sign" in response.json()["detail"][0]["ctx"]["reason"]


def test_access_protected_route_with_invalid_token(client, test_user: User):
    invalid_token = "expired_api_key_example"
    response = client.get(
        "/auth/protected-route",
        headers={"Authorization": f"Bearer {invalid_token}"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"

def test_delete_account(client):
    response = client.post(
        "/auth/user/login",
        json={
            "email": "newuser@example.com", 
            "password": "newpassword"
        }
    )
    assert "api_key" in response.json()
    api_key = response.json()["api_key"]
    response = client.delete(
        "/auth/account",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    assert response.status_code == 200
    assert response.json()["detail"].startswith("Deleted account")

# Example user data, which you would typically get from the database
fake_usernme = {"sub": "nonexistentusername"}
no_data = {}

# Generate the access token
invalid_api_key = create_api_key(data=fake_usernme)

def test_delete_nonexistent_account(client):
    response = client.delete(
        "/auth/account",
        headers={"Authorization": f"Bearer {invalid_api_key}"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"
