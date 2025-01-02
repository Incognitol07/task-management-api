# app/routers/profile.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.schemas import (
    UserCreate,
    UserLogin,
    RegisterResponse,
    LoginResponse,
    DetailResponse,
    RefreshResponse,
    RefreshToken
)
from app.models import (
    User
)
from app.utils import (
    logger,
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    get_current_user
)
from app.database import get_db

# Create an instance of APIRouter to handle authentication routes
router = APIRouter()