from contextlib import asynccontextmanager

import stripe
from fastapi import FastAPI

from app.config import get_settings
from app.routers.webhook_router import router as webhook_router
from app.services import event_store


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    stripe.api_key = settings.stripe_secret_key
    event_store.init_db()
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="Order Confirmation", lifespan=lifespan)
    app.include_router(webhook_router)
    return app
