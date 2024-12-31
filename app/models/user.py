# app/models/user.py

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class User(Base):
    """
    Represents a user of the Task Management API.

    Attributes:
        id (Integer): Unique identifier for each user.
        username (String): Username of the user.
        email (String): Email of the user.
        password_hash (String): Hashed password for user authentication.
        created_at (DateTime): Timestamp of user creation.
        updated_at (DateTime): Timestamp of last user update.

    Relationships:
        tasks (Task): List of tasks associated with the user.
        notifications (Notification): List of notifications associated with the user.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    # Relationships
    tasks = relationship("Task", back_populates="owner")
    notifications = relationship("Notification", back_populates="user")
