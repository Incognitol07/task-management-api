from sqlalchemy.orm import Session
from app.models import (
    Notification
)
from datetime import datetime
from uuid import UUID

def send_notification(db: Session, user_id: UUID, message: str, task_id:UUID):
    notification = Notification(
        user_id=user_id,
        message=message,
        sent_at = datetime.now(),
        task_id = task_id
    )
    db.add(notification)
    db.commit()