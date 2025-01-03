# app/models/notification.py

import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Notification(Base):
    """
    Represents a notification for a task in the Task Management API.

    Attributes:
        id (Integer): Unique identifier for each notification.
        message (String): Content of the notification.
        task_id (Integer): Foreign key linking to the task associated with the notification.
        user_id (Integer): Foreign key linking to the user associated with the notification.
        is_read (Boolean): Indicates whether the notification has been read.
        created_at (DateTime): Timestamp of notification creation.
        sent_at (DateTime): Timestamp of when the notification was sent.
    """

    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    message = Column(String, nullable=False)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    sent_at = Column(DateTime, nullable=True)

    # Relationships
    task = relationship("Task", back_populates="notifications")
    user = relationship("User", back_populates="notifications")
