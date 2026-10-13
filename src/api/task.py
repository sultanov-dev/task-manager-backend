from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_current_user, get_db
from src.models.auth import UsersModel
from src.schemas.tasks import TaskRequest, TaskResponse, TaskSchema
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


@router.get(
    "/{task_id}", response_model=dict[str, TaskSchema], status_code=status.HTTP_200_OK
)
async def get_taks_by_id(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UsersModel, Depends(get_current_user)],
    task_id: Annotated[UUID, Path(description="ID bo'yicha bitta taskni qaytaradi")],
):
    return await tasks_service.get_one_task(db, current_user, task_id)


@router.patch(
    "/{task_id}", response_model=dict[str, TaskResponse], status_code=status.HTTP_200_OK
)
async def update_task(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UsersModel, Depends(get_current_user)],
    task_id: Annotated[UUID, Path(description="ID bo'yicha bitta taskni yangilaydi")],
    payload: TaskRequest,
):
    return await tasks_service.update_task(db, current_user, task_id, payload)
