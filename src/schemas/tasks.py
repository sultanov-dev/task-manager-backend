from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.models.enums import Priority, TaskStatus


class TaskSchema(BaseModel):
    id: UUID
    title: str = Field(..., min_length=3, max_length=120, title="BO'lishi kerak")
    description: str | None = Field(max_length=210)
    status: TaskStatus = TaskStatus.TODO
    priority: Priority = Priority.LOW
    due_date: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class TaskRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
    priority: Priority | None = None
    due_date: datetime | None = None


class TaskResponse(BaseModel):
    title: str = Field(..., min_length=3, max_length=120, title="BO'lishi kerak")
    description: str | None = Field(max_length=210)
    status: TaskStatus = TaskStatus.TODO
    priority: Priority = Priority.LOW
    due_date: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class TaskFilters(BaseModel):
    status: TaskStatus | None = None
    priority: Priority | None = None
