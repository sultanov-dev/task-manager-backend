from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.auth import UsersModel
from src.models.task import Priority, TasksModel, TaskStatus


async def seed_tasks(db: AsyncSession) -> int:
    result = await db.execute(select(UsersModel).limit(1))
    user = result.scalar_one_or_none()

    if user is None:
        raise ValueError("Database'da user mavjud emas. Avval user yarating.")

    seed_data = [
        {
            "title": "FastAPI authentication yozish",
            "description": "JWT orqali foydalanuvchini autentifikatsiya qilish.",
            "status": TaskStatus.DONE,
            "priority": Priority.HIGH,
        },
        {
            "title": "Task Manager API testlarini yozish",
            "description": "Pytest yordamida endpointlarni tekshirish.",
            "status": TaskStatus.TODO,
            "priority": Priority.MEDIUM,
        },
        {
            "title": "Database backup qilish",
            "description": "PostgreSQL ma'lumotlar bazasining zaxira nusxasini yaratish.",
            "status": TaskStatus.TODO,
            "priority": Priority.HIGH,
        },
        {
            "title": "Dashboard dizaynini tayyorlash",
            "description": "Tasklar statistikasi uchun dashboard interfeysini yaratish.",
            "status": TaskStatus.IN_PROGRESS,
            "priority": Priority.MEDIUM,
        },
        {
            "title": "README faylini yozish",
            "description": "Loyihani o'rnatish va ishga tushirish bo'yicha ko'rsatmalar yozish.",
            "status": TaskStatus.DONE,
            "priority": Priority.LOW,
        },
        {
            "title": "Email orqali parolni tiklash",
            "description": "Parolni unutgan foydalanuvchilar uchun tiklash funksiyasini yaratish.",
            "status": TaskStatus.TODO,
            "priority": Priority.HIGH,
        },
        {
            "title": "SQLAlchemy query'larini optimallashtirish",
            "description": "Keraksiz database so'rovlarini kamaytirish.",
            "status": TaskStatus.IN_PROGRESS,
            "priority": Priority.HIGH,
        },
        {
            "title": "Profilni tahrirlash endpointi",
            "description": "Foydalanuvchiga ismi va boshqa profil ma'lumotlarini yangilash imkonini berish.",
            "status": TaskStatus.TODO,
            "priority": Priority.MEDIUM,
        },
        {
            "title": "Alembic migratsiyalarini tekshirish",
            "description": "Database sxemasi va migratsiyalar holatini tekshirish.",
            "status": TaskStatus.DONE,
            "priority": Priority.LOW,
        },
        {
            "title": "Tasklarni qidirish funksiyasi",
            "description": "Tasklarni sarlavhasi bo'yicha qidirish imkonini yaratish.",
            "status": TaskStatus.IN_PROGRESS,
            "priority": Priority.MEDIUM,
        },
        {
            "title": "Refresh token mexanizmi",
            "description": "Access token muddati tugaganda yangi token olishni tashkil qilish.",
            "status": TaskStatus.TODO,
            "priority": Priority.HIGH,
        },
        {
            "title": "API xatolarini standartlashtirish",
            "description": "HTTP xatolari uchun bir xil response formatini joriy qilish.",
            "status": TaskStatus.TODO,
            "priority": Priority.MEDIUM,
        },
        {
            "title": "Tasklarni priority bo'yicha saralash",
            "description": "Tasklar ro'yxatini ustuvorlik darajasi bo'yicha tartiblash.",
            "status": TaskStatus.DONE,
            "priority": Priority.LOW,
        },
        {
            "title": "Pagination qo'shish",
            "description": "Tasklar ro'yxatini limit va offset orqali sahifalash.",
            "status": TaskStatus.IN_PROGRESS,
            "priority": Priority.MEDIUM,
        },
        {
            "title": "CORS sozlamalarini tekshirish",
            "description": "Frontend va backend o'rtasidagi so'rovlarni to'g'ri sozlash.",
            "status": TaskStatus.TODO,
            "priority": Priority.LOW,
        },
        {
            "title": "Foydalanuvchi ruxsatlarini tekshirish",
            "description": "Har bir foydalanuvchi faqat o'z tasklarini boshqara olishini tekshirish.",
            "status": TaskStatus.IN_PROGRESS,
            "priority": Priority.HIGH,
        },
        {
            "title": "Taskni o'chirish endpointi",
            "description": "Taskni ID orqali topish va database'dan o'chirish.",
            "status": TaskStatus.DONE,
            "priority": Priority.MEDIUM,
        },
        {
            "title": "API hujjatlarini yaxshilash",
            "description": "Swagger interfeysida endpointlar uchun tushunarli tavsiflar yozish.",
            "status": TaskStatus.TODO,
            "priority": Priority.LOW,
        },
        {
            "title": "Async database ulanishini tekshirish",
            "description": "Database session ochilishi va yopilishi to'g'ri ishlashini tekshirish.",
            "status": TaskStatus.DONE,
            "priority": Priority.HIGH,
        },
        {
            "title": "Task statistikasi endpointi",
            "description": "Bajarilgan, bajarilayotgan va kutilayotgan tasklar sonini hisoblash.",
            "status": TaskStatus.TODO,
            "priority": Priority.MEDIUM,
        },
    ]

    result = await db.execute(
        select(TasksModel.title).where(TasksModel.user_id == user.id)
    )
    existing_titles = set(result.scalars().all())

    new_tasks = [
        TasksModel(
            **task_data,
            user_id=user.id,
            due_date=datetime.now(UTC) + timedelta(days=index + 1),
        )
        for index, task_data in enumerate(seed_data)
        if task_data["title"] not in existing_titles
    ]

    if not new_tasks:
        print("Barcha seed tasklar allaqachon mavjud.")
        return 0

    db.add_all(new_tasks)
    await db.commit()

    print(f"{len(new_tasks)} ta task yaratildi. User ID: {user.name}")

    return len(new_tasks)
