# app/routers/task.py

from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.schemas import DetailResponse, CreateTask, TaskResponse
from app.models import User, Task, TaskDependency
from app.utils import logger, get_current_user, set_cache, get_cache, delete_cache
from app.database import get_db
import json
from fastapi_limiter.depends import RateLimiter
from app.background_tasks import create_recurring_tasks, send_task_reminders

# Create an instance of APIRouter to handle task routes
router = APIRouter()

# Rate limiter for endpoints (e.g., max 5 requests per minute per user)
rate_limiter = RateLimiter(times=1000, minutes=1)
@router.get("/", response_model=list[TaskResponse], dependencies=[Depends(rate_limiter)])
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



@router.get("/{task_id}", response_model=TaskResponse, dependencies=[Depends(rate_limiter)])
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


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
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


@router.put("/{task_id}", response_model=TaskResponse)
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


@router.delete("/{task_id}", response_model=DetailResponse)
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


@router.get("/recurring")
async def get_recurring_tasks(db: Session = Depends(get_db)):
    """Retrieve a list of all recurring tasks."""
    recurring_tasks = db.query(Task).filter(Task.is_recurring == True).all()
    if not recurring_tasks:
        raise HTTPException(status_code=404, detail="No recurring tasks found")
    return recurring_tasks

@router.put("/{task_id}/recurrence")
async def update_recurrence(
    task_id: int, recurrence_interval: str, db: Session = Depends(get_db)
):
    """Update the recurrence interval or other settings for a recurring task."""
    task = db.query(Task).filter(Task.id == task_id, Task.is_recurring == True).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Update the recurrence settings
    task.recurrence_interval = recurrence_interval
    db.commit()
    db.refresh(task)
    
    return {"message": "Recurrence settings updated", "task": task}

@router.get("/{task_id}/recurrence")
async def get_task_recurrence(
    task_id: int, db: Session = Depends(get_db)
):
    """Update the recurrence interval or other settings for a recurring task."""
    task = db.query(Task).filter(Task.id == task_id, Task.is_recurring == True).first()
    
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    return {"task": task}

@router.post("/reminders")
async def run_reminders():
    """Triggers a manual reminder for tasks due soon."""
    send_task_reminders.delay()  # Trigger the Celery task asynchronously
    return {"message": "Reminder task triggered."}

@router.post("/run-recurring")
async def run_recurring_tasks():
    """Triggers the manual creation of recurring tasks."""
    create_recurring_tasks.delay()  # Trigger the Celery task asynchronously
    return {"message": "Recurring tasks creation triggered."}


# Add a dependency to a task
@router.post("/{task_id}/dependencies", response_model=TaskResponse)
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
@router.get("/{task_id}/dependencies", response_model=list[TaskResponse])
async def get_task_dependencies(
    task_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Retrieves a list of tasks that the specified task depends on.
    """
    try:
        task = db.query(Task).filter(Task.id == task_id, Task.user_id == user.id).first()

        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        dependencies = db.query(Task).join(
            TaskDependency, TaskDependency.dependent_task_id == Task.id
        ).filter(TaskDependency.task_id == task_id).all()

        return dependencies
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

# Remove a dependency from a task
@router.delete("/{task_id}/dependencies/{dependent_task_id}", response_model=TaskResponse)
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
