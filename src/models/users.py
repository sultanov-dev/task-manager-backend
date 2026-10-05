from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin
from src.models.task import TasksModel


class UsersModel(Base):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(100), nullable=False)

    tasks: Mapped[list["TasksModel"]] = relationship(
        back_populates="users",
        cascade="all, delete-orphan",
    )

    created_at = TimestampMixin.created_at
    upadated_at = TimestampMixin.updated_at
