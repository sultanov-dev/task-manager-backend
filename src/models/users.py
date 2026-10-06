from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.models.task import TasksModel


class UsersModel(TimestampMixin, Base):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(100), nullable=False)

    tasks: Mapped[list["TasksModel"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
