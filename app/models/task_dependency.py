# app/models/task_dependency.py

import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, ForeignKey
from app.database import Base


class TaskDependency(Base):
    """
    Represents a dependency between two tasks in the Task Management API.

    Attributes:
        id (Integer): Unique identifier for each task dependency.
        task_id (Integer): Foreign key linking to the dependent task.
        dependent_task_id (Integer): Foreign key linking to the parent task.
    """

    __tablename__ = "task_dependencies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False)
    dependent_task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False)
