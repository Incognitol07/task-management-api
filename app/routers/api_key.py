# app/routers/api_key.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas import (
    APIKeyResponse,
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

@router.post("/regenerate", response_model=APIKeyResponse)
def regenerate_api_key(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """
    Regenerates a new API key for the authenticated user.

    Args:
        db (Session): Database session for querying and modifying the database.
        current_user (User): The currently authenticated user.

    Returns:
        APIKeyResponse: Success message with the new API key.
    """
    new_api_key = create_api_key(data={"sub": current_user.username})
    current_user.api_key = new_api_key
    db.commit()
    db.refresh(current_user)

    logger.info(f"API key regenerated for user: {current_user.username}")
    return {
        "detail": "API key regenerated successfully",
        "api_key": new_api_key,
    }


@router.post("/revoke", response_model=APIKeyResponse)
def revoke_api_key(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """
    Revokes the API key of the authenticated user.

    Args:
        db (Session): Database session for querying and modifying the database.
        current_user (User): The currently authenticated user.

    Returns:
        APIKeyResponse: Success message confirming revocation.
    """
    current_user.api_key = None
    db.commit()
    db.refresh(current_user)

    logger.info(f"API key revoked for user: {current_user.username}")
    return {"detail": "API key revoked successfully"}
