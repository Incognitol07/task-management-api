# app/utils/security.py

import jwt
from fastapi import Depends, HTTPException, status
from datetime import datetime, timedelta
from passlib.context import CryptContext
from .logging_config import logger
from ..config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Hash a password
def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt hashing algorithm.

    Args: \n
        password (str): The plain text password to be hashed.

    Returns:
        str: The hashed password.
    """
    return pwd_context.hash(password)


# Verify a password against its hashed version
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify if the provided password matches the hashed password.

    Args: \n
        plain_password (str): The plain text password.
        hashed_password (str): The hashed password to compare with.

    Returns:
        bool: True if the passwords match, otherwise False.
    """
    return pwd_context.verify(plain_password, hashed_password)


# JWT configuration
SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = "HS256"

# Token Expiry Configuration
ACCESS_TOKEN_EXPIRE_MINUTES = 43200  # 30 days in minutes

# Secret Key Validation
if not SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY environment variable is not set.")

def create_api_key(data: dict) -> str:
    """
    Generate a JWT token with the given data payload.

    Args:
        data (dict): Data to encode into the JWT.

    Returns:
        str: Encoded JWT token.
    """
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_api_key(token: str) -> dict:
    """
    Verify and decode a JWT token.

    Args:
        token (str): JWT token to verify.

    Returns:
        dict: Decoded payload if valid.

    Raises:
        HTTPException: If the token is expired, invalid, or malformed.
    """
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        logger.warning("Expired token: %s", token)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        logger.error("Invalid or malformed token: %s", token)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or malformed token",
            headers={"WWW-Authenticate": "Bearer"},
        )
