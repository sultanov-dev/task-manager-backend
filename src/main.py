from fastapi import FastAPI, Response

from src.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
)


@app.get("/health")
def health():
    return Response(status_code=200)
