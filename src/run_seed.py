import asyncio

from src.database import async_session
from src.seed import seed_tasks


async def main():
    async with async_session() as db:
        await seed_tasks(db)


if __name__ == "__main__":
    asyncio.run(main())
