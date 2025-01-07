# app/routers/profile.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.schemas import (
    UserCreate,
    UserLogin,
    RegisterResponse,
    LoginResponse,
    DetailResponse
)
from app.models import (
    User
)
from app.utils import (
    logger,
    get_current_user
)
from app.database import get_db

# Create an instance of APIRouter to handle authentication routes
router = APIRouter()

@router.get("/")
async def get_profile():
    ...