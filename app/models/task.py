# app/models/task.py

import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
from enum import Enum as PyEnum


# Define the priority options using Python's Enum
class TaskPriority(PyEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

# Define the status options using Python's Enum
class TaskStatus(PyEnum):
    PENDING = "pending"
    COMPLETE = "complete"
    IN_PROGRESS = "in_progress"

# Define the recurrence interval options using Python's Enum
class RecurringInterval(PyEnum):
    DAILY = "daily"
    BI_WEEKLY = "bi_weekly"  # New option
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"  # New option
    YEARLY = "yearly"


class Task(Base):
    """
    Represents a task in the Task Management API.

    Attributes:
        id (UUID): Unique identifier for each task.
        title (String): Title of the task.
        description (String): Description of the task.
        due_date (DateTime): Due date for the task.
        status (Enum): Status of the task (e.g., Pending, Complete, In Progress).
        priority (Enum): Priority level of the task (e.g., Low, Medium, High).
        is_recurring (Boolean): Indicates if the task is recurring.
        recurrence_interval (Enum): Interval for recurring tasks (e.g., daily, bi-weekly, quarterly).
        user_id (UUID): Foreign key linking to the user who owns the task.
        created_at (DateTime): Timestamp of task creation.
        updated_at (DateTime): Timestamp of last task update.

    Relationships:
        owner (User): Reference to the User who owns the task.
        notifications (Notification): List of notifications associated with the task.
    """

    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    due_date = Column(DateTime, nullable=False)
    status = Column(Enum(TaskStatus), nullable=False, default=TaskStatus.PENDING)
    priority = Column(Enum(TaskPriority), nullable=False, default=TaskPriority.MEDIUM)
    is_recurring = Column(Boolean, default=False, nullable=False)
    recurrence_interval = Column(Enum(RecurringInterval), nullable=True)  # Updated to include new intervals
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    # Relationships
    owner = relationship("User", back_populates="tasks")
    notifications = relationship("Notification", back_populates="task")

    def recurrence_description(self):
        """
        A helper method to describe the recurrence pattern for the task.

        Returns:
            str: A human-readable description of the recurrence pattern.
        """
        if self.is_recurring and self.recurrence_interval:
            interval_mapping = {
                "daily": "day",
                "bi_weekly": "two weeks",
                "weekly": "week",
                "monthly": "month",
                "quarterly": "three months",
                "yearly": "year",
            }
            interval = self.recurrence_interval.value
            return f"Repeats every {interval_mapping[interval]}"
        return "Non-recurring task"

    def to_dict(self):
        """Convert the SQLAlchemy object to a dictionary."""
        return {
            "id": str(self.id),  # Convert UUID to string for JSON serialization
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date.isoformat() if self.due_date else None,  # Format datetime as string
            "status": self.status.value,  # Enum value as string
            "priority": self.priority.value,  # Enum value as string
            "is_recurring": self.is_recurring,
            "recurrence_interval": self.recurrence_interval.value if self.recurrence_interval else None,
            "recurrence_description": self.recurrence_description(),  # Include the custom description
            "user_id": str(self.user_id),  # Convert UUID to string
            "created_at": self.created_at.isoformat(),  # Format datetime as string
            "updated_at": self.updated_at.isoformat(),  # Format datetime as string
        }
