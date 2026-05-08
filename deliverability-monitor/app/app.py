from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import get_settings
from app.database import Base, engine
from app.routers.webhook_router import router as webhook_router
from app.services.scheduler import create_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    settings = get_settings()
    scheduler = create_scheduler(settings)
    scheduler.start()
    yield
    scheduler.shutdown()


def create_app() -> FastAPI:
    app = FastAPI(title="Deliverability Monitor", lifespan=lifespan)
    app.include_router(webhook_router)
    return app
