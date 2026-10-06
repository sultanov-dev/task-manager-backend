from contextlib import asynccontextmanager

from fastapi import FastAPI, Response

from src.core.config import settings
from src.database import engine
from src.models.base import Base


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield
    await engine.dispose()


app = FastAPI(
    lifespan=lifespan,
    title=settings.APP_NAME,
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
)


@app.get("/health")
def health():
    return Response(status_code=200)
