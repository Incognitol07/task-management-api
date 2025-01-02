# app/schemas/notifications.py

from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional

class NotificationResponse(BaseModel):
    id: UUID
    message: str
    is_read: bool
    task_id: UUID
    is_read: bool
    created_at: datetime
    sent_at: Optional[datetime]

    class Config:
        from_attributes = True
