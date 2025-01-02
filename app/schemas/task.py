from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from app.models import TaskPriority, TaskStatus
from typing import Optional

class CreateTask(BaseModel):
    title: str
    description: str
    due_date: datetime
    status: TaskStatus
    priority: TaskPriority
    is_recurring: bool = False
    recurrence_interval: Optional[str] = None

class TaskResponse(BaseModel):
    id: UUID
    title: str
    description: str
    due_date: datetime
    status: TaskStatus
    priority: TaskPriority
    is_recurring: bool = False
    recurrence_interval: Optional[str] = None
    created_at: datetime
    updated_at: datetime