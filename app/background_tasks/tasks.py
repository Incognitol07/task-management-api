# app/background_jobs/tasks.py

from datetime import datetime, timedelta
from app.models.task import Task, TaskStatus, RecurringInterval
from app.database import SessionLocal
from app.utils import send_notification
from ..celery import celery_app

@celery_app.task
def create_recurring_tasks():
    """Automatically create recurring tasks based on their intervals."""
    db = SessionLocal()
    now = datetime.now()
    tasks = db.query(Task).filter(Task.is_recurring == True).all()

    for task in tasks:
        interval = task.recurrence_interval

        # Calculate the next due date based on the recurrence interval
        if interval == RecurringInterval.DAILY.value:
            next_due_date = task.due_date + timedelta(days=1)
        elif interval == RecurringInterval.BI_WEEKLY.value:
            next_due_date = task.due_date + timedelta(weeks=2)
        elif interval == RecurringInterval.WEEKLY.value:
            next_due_date = task.due_date + timedelta(weeks=1)
        elif interval == RecurringInterval.MONTHLY.value:
            next_due_date = task.due_date + timedelta(days=30)  # Approximate month
        elif interval == RecurringInterval.QUARTERLY.value:
            next_due_date = task.due_date + timedelta(days=90)  # Approximate quarter
        elif interval == RecurringInterval.YEARLY.value:
            next_due_date = task.due_date + timedelta(days=365)
        else:
            continue

        # Create a new task for the next interval
        new_task = Task(
            title=task.title,
            description=task.description,
            due_date=next_due_date,
            is_recurring=False,  # Newly created tasks are not recurring
            status=TaskStatus.PENDING,
            user_id=task.user_id,
            priority=task.priority,
        )
        db.add(new_task)

    db.commit()
    db.close()

@celery_app.task
def send_task_reminders():
    """Send reminders for tasks due within the next hour."""
    db = SessionLocal()
    now = datetime.now()
    reminder_time = now + timedelta(hours=1)

    tasks = db.query(Task).filter(
        Task.due_date <= reminder_time,
        Task.status == TaskStatus.PENDING
    ).all()

    sent_notifications = []
    for task in tasks:
        try:
            send_notification(
                db=db,
                user_id=task.user_id,
                message=f"Reminder: Task '{task.title}' is due at {task.due_date}.",
                task_id=task.id
            )
            sent_notifications.append(task.id)  # Collect the task ID
        except Exception as e:
            # Log the error or handle it
            print(f"Failed to send notification for task {task.id}: {e}")

    db.close()
    return {"sent_notifications": sent_notifications, "count": len(sent_notifications)}

