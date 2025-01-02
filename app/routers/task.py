# app/routers/task.py

from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from sqlalchemy.orm import Session
from app.schemas import (
    DetailResponse, 
    CreateTask,
    TaskResponse
)
from app.models import (
    User,
    Task
)
from app.utils import (
    logger,
    get_current_user
)
from app.database import get_db

# Create an instance of APIRouter to handle task routes
router = APIRouter()

@router.post("/", response_model=TaskResponse)
async def create_task(
    task: CreateTask,
    db: Session = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    new_task = Task(**task.model_dump(), user_id=user.id)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@router.get("/", response_model=list[TaskResponse])
async def get_tasks(
    db: Session = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    tasks =  db.query(Task).filter(Task.user_id == user.id).all()
    return tasks

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    db: Session = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    task =  db.query(Task).filter(Task.user_id == user.id, Task.id == task_id).first()
    return task

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    db: Session = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    ...

@router.delete("/{task_id}", response_model=DetailResponse)
async def delete_task(
    task_id: UUID,
    db: Session = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    ...