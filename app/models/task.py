from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Task(Base):
    """
    Represents a task in the Task Management API.

    Attributes:
        id (Integer): Unique identifier for each task.
        title (String): Title of the task.
        description (String): Description of the task.
        due_date (DateTime): Due date for the task.
        status (String): Status of the task (e.g., Pending, Completed, Overdue).
        priority (String): Priority level of the task (e.g., Low, Medium, High).
        is_recurring (Boolean): Indicates if the task is recurring.
        recurrence_interval (String): Interval for recurring tasks (e.g., daily, weekly, monthly).
        user_id (Integer): Foreign key linking to the user who owns the task.
        created_at (DateTime): Timestamp of task creation.
        updated_at (DateTime): Timestamp of last task update.

    Relationships:
        owner (User): Reference to the User who owns the task.
        notifications (Notification): List of notifications associated with the task.
    """

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    due_date = Column(DateTime, nullable=False)
    status = Column(String, default="Pending", nullable=False)
    priority = Column(String, default="Medium", nullable=False)
    is_recurring = Column(Boolean, default=False, nullable=False)
    recurrence_interval = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    # Relationships
    owner = relationship("User", back_populates="tasks")
    notifications = relationship("Notification", back_populates="task")
