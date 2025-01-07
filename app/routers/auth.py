# app/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.schemas import (
    UserCreate,
    UserLogin,
    RegisterResponse,
    LoginResponse,
    DetailResponse,
)
from app.models import (
    User
)
from app.utils import (
    logger,
    hash_password,
    verify_password,
    create_api_key,
    get_current_user
)
from app.database import get_db

# Create an instance of APIRouter to handle authentication routes
router = APIRouter()




# Register route to create a new user account
@router.post("/register", response_model=RegisterResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Registers a new user account.

    Args: \n
        user (UserCreate): The user data containing the username, email, and password.
        db (Session): The database session to check for existing users and add new ones.

    Raises:
        HTTPException: If the username is already registered.

    Returns:
        User: The newly created user object.
    """
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        logger.warning(f"Attempt to register with an existing username: {user.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    db_email = db.query(User).filter(User.email == user.email).first()
    if db_email:
        logger.warning(f"Attempt to register with an existing email: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash the password before storing
    hashed_password = hash_password(user.password)

    # Generate API Key
    api_key = create_api_key(data={"sub": user.username})

    new_user = User(
        username=user.username, 
        email=user.email, 
        hashed_password=hashed_password,
        api_key = api_key
    )

    # Add the new user to the database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    db_user = (
        db.query(User)
        .filter(
            User.username == user.username, 
            User.hashed_password == hashed_password
        )
        .first()
    )

    logger.info(
        f"New user registered successfully: {new_user.username} ({new_user.email})."
    )
    return {
        "username": user.username,
        "email": user.email,
        "message": "Registered successfully"
    }


# Login route for user authentication and token generation
@router.post("/user/login", response_model=LoginResponse)
async def user_login(user: UserLogin, db: Session = Depends(get_db)):
    """
    Logs in a user by verifying the username and password, and returning a JWT access token.

    Args: \n
        user (UserLogin): The user data containing the email and password.
        db (Session): The database session to validate user credentials.

    Raises:
        HTTPException: If the credentials are invalid.

    Returns:
        dict: A dictionary containing the access token and token type.
    """
    # Query the database for the user and verify password
    db_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if not db_user or not verify_password(user.password, db_user.hashed_password):
        logger.warning(f"Failed login attempt for email: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials"
        )
    

    #Get API Key
    api_key = db_user.api_key

    logger.info(f"User '{db_user.username}' logged in successfully.")
    return {
        "api_key": api_key,
        "token_type": "bearer",
        "username": db_user.username
    }


# Protected route example requiring authentication
@router.get("/protected-route", response_model=DetailResponse)
async def protected_route(current_user: User = Depends(get_current_user)):
    """
    A protected route that can only be accessed by authenticated users.

    Args: \n
        current_user (User): The currently authenticated user, provided by the `get_current_user` dependency.

    Returns:
        dict: A greeting message with the username of the authenticated user.
    """
    return {
        "detail": f"Hello, {current_user.username}! You have access to this protected route."
    }


@router.delete("/account", response_model=DetailResponse)
def delete_account(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    """
    Deletes a user along with their associated data.

    Args: \n
        db (Session): Database session for querying and modifying the database.
        user (user): The current user.

    Raises:
        HTTPException: If the user does not exist.

    Returns:
        DetailResponse: Success message confirming the user deletion.
    """
    target_user = db.query(User).filter(User.id == user.id).first()

    if not target_user:
        logger.warning(
            f"Attempted deletion of account with ID: {user.id} by user '{user.username}'."
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    db.delete(target_user)
    db.commit()
    logger.info(f"User '{user.username}' deleted account (ID: {user.id}).")
    return {"detail": f"Deleted account of '{target_user.username}' successfully"}


# Login route for user authentication and token generation
@router.post("/login")
async def login_for_oauth_form(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """Login for /docs . please DO NOT USE THIS ROUTE AT ALL
    """
    db_user = db.query(User).filter(User.email == form_data.username).first()

    if not db_user or not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials"
        )

    # Create and return the API Key
    access_token = create_api_key(data={"sub": db_user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": db_user.username,
    }
