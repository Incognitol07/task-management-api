# app/models/user.py

import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, DateTime
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

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    api_key = Column(String, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    # Relationships
    tasks = relationship("Task", back_populates="owner")
    notifications = relationship("Notification", back_populates="user")
