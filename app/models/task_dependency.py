# app/models/task_dependency.py

from sqlalchemy import Column, Integer, ForeignKey
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

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    dependent_task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
