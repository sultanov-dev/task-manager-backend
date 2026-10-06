from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin
from src.models.enums import Priority, TaskStatus

if TYPE_CHECKING:
    from src.models.users import UsersModel


class TasksModel(TimestampMixin, Base):
    __tablename__ = "tasks"

    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(290))
    status: Mapped[TaskStatus] = mapped_column(
        SQLEnum(TaskStatus, name="tasks_status", native_enum=True),
        default=TaskStatus.TODO,
        nullable=False,
    )
    priority: Mapped[Priority] = mapped_column(
        SQLEnum(Priority, name="tasks_priority", native_enum=True),
        default=Priority.LOW,
        nullable=False,
    )
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    user: Mapped["UsersModel"] = relationship(back_populates="tasks")
