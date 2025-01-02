# tests/test_auth.py
from app.utils import create_refresh_token, create_access_token


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

def test_register_existing_user(client, test_user):
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

def test_login_user(client, test_user):
    response = client.post(
        "/auth/user/login",
        json={
            "email": test_user.email, 
            "password": "testpassword"
        },
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()


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

def test_protected_route(client, test_user):
    # Login to get an access token
    login_response = client.post(
        "/auth/user/login",
        json={
            "email": test_user.email, 
            "password": "testpassword"
        },
    )
    access_token = login_response.json()["access_token"]

    # Use the access token to access a protected route
    response = client.get(
        "/auth/protected-route",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    assert response.json()["detail"].startswith("Hello, testuser!")

def test_refresh_token(client, test_user):
    # Login to get a refresh token
    login_response = client.post(
        "/auth/user/login",
        json={"email": test_user.email, "password": "testpassword"},
    )
    refresh_token = login_response.json()["refresh_token"]

    # Use the refresh token to get a new access token
    response = client.post(
        "/auth/user/refresh-token",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

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


def test_access_protected_route_with_invalid_token(client, test_user):
    invalid_token = "expired_access_token_example"
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
    assert "access_token" in response.json()
    access_token = response.json()["access_token"]
    response = client.delete(
        "/auth/account",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    assert response.json()["detail"].startswith("Deleted account")

# Example user data, which you would typically get from the database
fake_email = {"sub": "nonexistent@gmail.com"}
no_data = {}

# Generate the access token
invalid_access_token = create_access_token(data=fake_email)

# Generate the refresh token (you would also pass user data)
invalid_refresh_token = create_refresh_token(data=no_data)

def test_delete_nonexistent_account(client):
    response = client.delete(
        "/auth/account",
        headers={"Authorization": f"Bearer {invalid_access_token}"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"

def test_refresh_token_invalid_token(client):
    response = client.post(
        "/auth/user/refresh-token",
        json={"refresh_token": invalid_refresh_token},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid refresh token payload"

