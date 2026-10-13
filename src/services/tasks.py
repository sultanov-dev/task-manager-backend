from collections.abc import Sequence
from typing import Annotated
from uuid import UUID

from fastapi import HTTPException, Path, status
from fastapi.params import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_current_user, get_db
from src.models.auth import UsersModel
from src.models.task import TasksModel
from src.schemas.tasks import TaskSchema


async def task_create(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UsersModel, Depends(get_current_user)],
    payload: TaskSchema,
) -> TasksModel:
    try:
        new_task = TasksModel(
            title=payload.title,
            description=payload.description,
            status=payload.status,
            priority=payload.priority,
            due_date=payload.due_date,
            user_id=current_user.id,
        )

        db.add(new_task)
        await db.commit()
        await db.refresh(new_task)

        return new_task
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create task"
        ) from e


async def get_tasks(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UsersModel, Depends(get_current_user)],
) -> dict[str, Sequence[TasksModel]]:
    user_id = current_user.id
    result = await db.execute(
        select(TasksModel).where(TasksModel.user_id == str(user_id))
    )

    tasks = result.scalars().all()

    return {"tasks": tasks}


async def get_one_task(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UsersModel, Depends(get_current_user)],
    task_id: Annotated[UUID, Path(description="ID bo'yicha bitta taskni qaytaradi")],
) -> dict[str, TaskSchema]:
    if not task_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Task id berilmagan"
        )

    result = await db.execute(
        select(TasksModel).where(
            TasksModel.user_id == str(current_user.id), TasksModel.id == task_id
        )
    )

    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task topilmadi"
        )

    return {"task": TaskSchema.model_validate(task)}
