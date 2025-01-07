# app/routers/task_recurrence.py

import json
from fastapi_limiter.depends import RateLimiter
from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi_limiter.depends import RateLimiter
from app.models import User, Task
from app.utils import (
    logger, 
    get_current_user, 
    set_cache, 
    get_cache, 
    delete_cache
)
from app.schemas import TaskResponse, TaskRecurrenceChange
from app.database import get_db

rate_limiter = RateLimiter(times=1000, minutes=1)
# Create an instance of APIRouter to handle task routes
router = APIRouter()


@router.get("/", dependencies=[Depends(rate_limiter)])
async def get_all_recurring_tasks(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Retrieve a list of all recurring tasks."""
    try:
        cache_key = f"recurring-tasks:{current_user.id}"
        cached_tasks = await get_cache(cache_key)

        if cached_tasks:
            # Deserialize the cached JSON string into a list of TaskResponse objects
            tasks_data = json.loads(cached_tasks)  # Deserialize into a list of dicts
            return [TaskResponse(**task) for task in tasks_data]  # Convert to TaskResponse models
        recurring_tasks = db.query(Task).filter(Task.is_recurring == True, Task.user_id == current_user.id).all()
        if not recurring_tasks:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No recurring tasks found")
        serialized_tasks = [task.to_dict() for task in recurring_tasks]
        await set_cache(cache_key, serialized_tasks)  # Ensure you serialize to JSON format
        return recurring_tasks
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@router.put("/{task_id}/recurrence", dependencies=[Depends(rate_limiter)])
async def update_recurrence(
    task_id: UUID, 
    recurrence_data: TaskRecurrenceChange, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update the recurrence interval or other settings for a recurring task."""
    try:
        task = db.query(Task).filter(Task.id == task_id, Task.is_recurring == True, Task.user_id == current_user.id).first()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Update the recurrence settings
        task.recurrence_interval = recurrence_data.recurrence_interval
        db.commit()
        db.refresh(task)
        
        await delete_cache(f"recurring-tasks:{current_user.id}:{task_id}")
        await delete_cache(f"recurring-tasks:{current_user.id}")  # Invalidate task list cache

        return {"message": "Recurrence settings updated", "task": task}
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@router.get("/{task_id}/recurrence", dependencies=[Depends(rate_limiter)])
async def get_task_recurrence(
    task_id: UUID, db: Session = Depends(get_db),current_user: User = Depends(get_current_user)
):
    """Update the recurrence interval or other settings for a recurring task."""
    try:
        cache_key = f"task:{current_user.id}:{task_id}"
        cached_task = await get_cache(cache_key)

        if cached_task:
            task_data = json.loads(cached_task)  # Deserialize into a list of dicts
            return TaskResponse(**task_data) # Convert to TaskResponse models
        
        task = db.query(Task).filter(Task.id == task_id, Task.is_recurring == True, Task.user_id == current_user.id).first()        
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        
        # Serialize the task and set the cache
        serialized_task = task.to_dict()
        await set_cache(cache_key, serialized_task)
        return task
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

