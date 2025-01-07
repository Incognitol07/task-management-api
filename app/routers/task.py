# app/routers/task.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_limiter.depends import RateLimiter
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.schemas import DetailResponse, CreateTask, TaskResponse
from app.models import User, Task
from app.utils import logger, get_current_user, set_cache, get_cache, delete_cache
from app.database import get_db
import json

rate_limiter = RateLimiter(times=1000, minutes=1)
# Create an instance of APIRouter to handle task routes
router = APIRouter()

@router.get("/", response_model=list[TaskResponse], dependencies= [Depends(rate_limiter)])
async def get_tasks(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Retrieve all tasks for the current user, with caching.
    """
    try:
        cache_key = f"tasks:{user.id}"
        cached_tasks = await get_cache(cache_key)

        if cached_tasks:
            # Deserialize the cached JSON string into a list of TaskResponse objects
            tasks_data = json.loads(cached_tasks)  # Deserialize into a list of dicts
            return [TaskResponse(**task) for task in tasks_data]  # Convert to TaskResponse models

        # Fetch tasks from the database
        tasks = db.query(Task).filter(Task.user_id == user.id).all()
        if tasks:
            # Serialize the tasks and set the cache
            serialized_tasks = [task.to_dict() for task in tasks]
            await set_cache(cache_key, serialized_tasks)  # Ensure you serialize to JSON format

        return tasks
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")



@router.get("/{task_id}",  dependencies= [Depends(rate_limiter)] ,response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Retrieve a specific task for the current user, with caching.
    """
    try:
        cache_key = f"task:{user.id}:{task_id}"
        cached_task = await get_cache(cache_key)

        if cached_task:
            task_data = json.loads(cached_task)  # Deserialize into a list of dicts
            return TaskResponse(**task_data) # Convert to TaskResponse models

        # Fetch task from the database
        task = db.query(Task).filter(Task.user_id == user.id, Task.id == task_id).first()

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
            )

        # Serialize the task and set the cache
        serialized_task = task.to_dict()
        await set_cache(cache_key, serialized_task)
        return serialized_task
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")


@router.post("/",  dependencies= [Depends(rate_limiter)],response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: CreateTask,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Create a new task for the current user.
    """
    try:
        new_task = Task(**task.model_dump(), user_id=user.id)
        db.add(new_task)
        db.commit()
        db.refresh(new_task)

        # Invalidate cache for task list
        await delete_cache(f"tasks:{user.id}")
        return new_task.to_dict()  # Return serialized task
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")


@router.put("/{task_id}",  dependencies= [Depends(rate_limiter)], response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    updated_task: CreateTask,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Update an existing task for the current user.
    """
    try:
        task = db.query(Task).filter(Task.user_id == user.id, Task.id == task_id).first()

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
            )

        for key, value in updated_task.model_dump().items():
            setattr(task, key, value)

        db.commit()
        db.refresh(task)

        # Invalidate cache
        await delete_cache(f"task:{user.id}:{task_id}")
        await delete_cache(f"tasks:{user.id}")  # Invalidate task list cache
        return task
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")


@router.delete("/{task_id}", dependencies= [Depends(rate_limiter)], response_model=DetailResponse)
async def delete_task(
    task_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Delete a task for the current user.
    """
    try:
        task = db.query(Task).filter(Task.user_id == user.id, Task.id == task_id).first()

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
            )

        db.delete(task)
        db.commit()

        # Invalidate cache
        await delete_cache(f"task:{user.id}:{task_id}")
        await delete_cache(f"tasks:{user.id}")  # Invalidate task list cache
        return {"detail": "Task deleted"}
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
