# app/routers/automation.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.exc import SQLAlchemyError
from app.utils import logger, get_current_user, set_cache, get_cache, delete_cache
from app.database import get_db
import json
from app.background_tasks import create_recurring_tasks, send_task_reminders
# Create an instance of APIRouter to handle task routes
router = APIRouter()

# Rate Limiting Middleware
rate_limiter = RateLimiter(times=1000, minutes=1)

@router.post("/reminders", dependencies=[Depends(rate_limiter)])
async def run_reminders():
    """Triggers a manual reminder for tasks due soon."""
    send_task_reminders.delay()  # Trigger the Celery task asynchronously
    return {"message": "Reminder task triggered."}

@router.post("/run-recurring", dependencies=[Depends(rate_limiter)])
async def run_recurring_tasks():
    """Triggers the manual creation of recurring tasks."""
    create_recurring_tasks.delay()  # Trigger the Celery task asynchronously
    return {"message": "Recurring tasks creation triggered."}