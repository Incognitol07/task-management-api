from pydantic import BaseModel
from app.models import RecurringInterval

class TaskRecurrenceChange(BaseModel):
    recurrence_interval: RecurringInterval