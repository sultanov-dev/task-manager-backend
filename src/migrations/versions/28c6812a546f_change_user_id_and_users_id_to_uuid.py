"""change user_id and users.id to UUID

Revision ID: 28c6812a546f
Revises: ab40430ca304
Create Date: 2026-10-06 18:13:29.283213

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "28c6812a546f"
down_revision: Union[str, Sequence[str], None] = "ab40430ca304"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # 1. Tashqi kalit cheklovini olib tashlash
    op.drop_constraint("tasks_user_id_fkey", "tasks", type_="foreignkey")

    # 2. users.id ni UUID ga o'zgartirish (agar allaqachon UUID bo'lsa, bu blokni o'chiring)
    op.alter_column(
        "users",
        "id",
        existing_type=sa.Integer(),  # hozirgi turga qarab: sa.Integer() yoki sa.String()
        type_=postgresql.UUID(as_uuid=True),
        existing_nullable=False,
        postgresql_using="id::text::uuid",
    )

    # 3. tasks.user_id ni UUID ga o'zgartirish
    op.alter_column(
        "tasks",
        "user_id",
        existing_type=sa.Integer(),  # hozirgi turga qarab
        type_=postgresql.UUID(as_uuid=True),
        existing_nullable=True,  # NULL ruxsat berilgan bo'lsa True
        postgresql_using="user_id::text::uuid",
    )

    # 4. Tashqi kalitni qayta qo'shish
    op.create_foreign_key("tasks_user_id_fkey", "tasks", "users", ["user_id"], ["id"])


def downgrade():
    # 1. Cheklovni olib tashlash
    op.drop_constraint("tasks_user_id_fkey", "tasks", type_="foreignkey")

    # 2. tasks.user_id ni eski turga qaytarish
    op.alter_column(
        "tasks",
        "user_id",
        existing_type=postgresql.UUID(as_uuid=True),
        type_=sa.Integer(),
        postgresql_using="user_id::text::integer",
    )

    # 3. users.id ni eski turga qaytarish
    op.alter_column(
        "users",
        "id",
        existing_type=postgresql.UUID(as_uuid=True),
        type_=sa.Integer(),
        postgresql_using="id::text::integer",
    )

    # 4. Cheklovni qayta qo'shish
    op.create_foreign_key("tasks_user_id_fkey", "tasks", "users", ["user_id"], ["id"])
