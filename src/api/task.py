from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_current_user, get_db
from src.models.auth import UsersModel
from src.models.task import TasksModel
from src.schemas.tasks import TaskSchema
from src.services import tasks as tasks_service

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


@router.post("/", response_model=TaskSchema, status_code=status.HTTP_201_CREATED)
async def task_create(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UsersModel, Depends(get_current_user)],
    payload: TaskSchema,
):
    return await tasks_service.task_create(db, current_user, payload)


@router.get(
    "/", response_model=dict[str, list[TaskSchema]], status_code=status.HTTP_200_OK
)
async def get_tasks(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UsersModel, Depends(get_current_user)],
):
    return await tasks_service.get_tasks(db, current_user)
