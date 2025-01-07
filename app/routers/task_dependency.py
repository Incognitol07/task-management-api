# app/routers/task_dependency.py

import json
from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi_limiter.depends import RateLimiter
from app.schemas import DetailResponse, CreateTask, TaskResponse
from app.models import User, Task, TaskDependency
from app.utils import logger, get_current_user, set_cache, get_cache, delete_cache
from app.database import get_db
# Create an instance of APIRouter to handle task routes
router = APIRouter()

# Rate Limiting Middleware
rate_limiter = RateLimiter(times=1000, minutes=1)

# Add a dependency to a task
@router.post("/{task_id}/dependencies/{dependent_task_id}", dependencies=[Depends(rate_limiter)], response_model=TaskResponse)
async def add_dependency_to_task(
    task_id: UUID,
    dependent_task_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Adds a dependent task to the specified task.
    """
    try:
        task = db.query(Task).filter(Task.id == task_id, Task.user_id == user.id).first()
        dependent_task = db.query(Task).filter(Task.id == dependent_task_id, Task.user_id == user.id).first()

        if not task or not dependent_task:
            raise HTTPException(status_code=404, detail="Task(s) not found")

        # Check if the dependency already exists
        existing_dependency = db.query(TaskDependency).filter(
            TaskDependency.task_id == task_id, TaskDependency.dependent_task_id == dependent_task_id
        ).first()

        if existing_dependency:
            raise HTTPException(status_code=400, detail="Dependency already exists")

        # Create new dependency
        new_dependency = TaskDependency(task_id=task_id, dependent_task_id=dependent_task_id)
        db.add(new_dependency)
        db.commit()

        # Return the updated task with dependencies
        task = db.query(Task).filter(Task.id == task_id).first()
        return task
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

# Get task dependencies
@router.get("/{task_id}/dependencies", dependencies=[Depends(rate_limiter)], response_model=list[TaskResponse])
async def get_task_dependencies(
    task_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Retrieves a list of tasks that the specified task depends on.
    """
    try:
        cache_key = f"dependent-tasks:{user.id}"
        cached_tasks = await get_cache(cache_key)

        if cached_tasks:
            # Deserialize the cached JSON string into a list of TaskResponse objects
            tasks_data = json.loads(cached_tasks)  # Deserialize into a list of dicts
            return [TaskResponse(**task) for task in tasks_data]  # Convert to TaskResponse models
        
        task = db.query(Task).filter(Task.id == task_id, Task.user_id == user.id).first()

        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        dependencies = db.query(Task).join(
            TaskDependency, TaskDependency.dependent_task_id == Task.id
        ).filter(TaskDependency.task_id == task_id).all()

        serialized_tasks = [task.to_dict() for task in dependencies]
        await set_cache(cache_key, serialized_tasks)  # Ensure you serialize to JSON format

        return dependencies
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

# Remove a dependency from a task
@router.delete("/{task_id}/dependencies/{dependent_task_id}", dependencies=[Depends(rate_limiter)],response_model=TaskResponse)
async def remove_dependency_from_task(
    task_id: UUID,
    dependent_task_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Removes a specific dependency for a task.
    """
    try:
        task = db.query(Task).filter(Task.id == task_id, Task.user_id == user.id).first()

        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        dependency = db.query(TaskDependency).filter(
            TaskDependency.task_id == task_id, TaskDependency.dependent_task_id == dependent_task_id
        ).first()

        if not dependency:
            raise HTTPException(status_code=404, detail="Dependency not found")

        db.delete(dependency)
        db.commit()

        # Return the updated task after removal of the dependency
        task = db.query(Task).filter(Task.id == task_id).first()
        return task
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
