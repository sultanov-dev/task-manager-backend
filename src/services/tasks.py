from collections.abc import Sequence
from typing import Annotated
from uuid import UUID

from fastapi import HTTPException, Path, Response, status
from fastapi.params import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_current_user, get_db, get_filters
from src.models.auth import UsersModel
from src.models.task import TasksModel
from src.schemas.tasks import TaskFilters, TaskRequest, TaskResponse, TaskSchema


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
    filters: Annotated[TaskFilters, Depends(get_filters)],
) -> dict[str, Sequence[TasksModel]]:
    user_id = current_user.id
    query = select(TasksModel).where(TasksModel.user_id == str(user_id))

    if filters.status is not None:
        query = query.where(TasksModel.status == filters.status)

    if filters.priority is not None:
        query = query.where(TasksModel.priority == filters.priority)

    result = await db.execute(query)
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


async def update_task(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UsersModel, Depends(get_current_user)],
    task_id: Annotated[UUID, Path(description="ID bo'yicha bitta taskni qaytaradi")],
    data: TaskRequest,
) -> dict[str, TaskResponse]:
    try:
        result = await db.execute(
            select(TasksModel).where(
                TasksModel.id == task_id, TasksModel.user_id == str(current_user.id)
            )
        )

        task = result.scalar_one_or_none()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Task topilmadi"
            )

        update_task = data.model_dump(exclude_unset=True)

        for key, value in update_task.items():
            setattr(task, key, value)

        await db.commit()
        await db.refresh(task)

        return {"task": TaskResponse.model_validate(task)}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to update task"
        ) from e


async def delete_task(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UsersModel, Depends(get_current_user)],
    task_id: Annotated[UUID, Path(description="ID bo'yicha bitta taskni o'chiradi")],
):
    try:
        result = await db.execute(
            select(TasksModel).where(
                TasksModel.id == task_id, TasksModel.user_id == str(current_user.id)
            )
        )
        task = result.scalar_one_or_none()

        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Task topilmadi"
            )

        await db.delete(task)
        await db.commit()

        response = Response()
        response.status_code = status.HTTP_204_NO_CONTENT

        return response

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to update task"
        ) from e
