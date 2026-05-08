from contextlib import asynccontextmanager

import stripe
from fastapi import FastAPI

from app.config import get_settings
from app.database import Base, SessionLocal, engine
from app.routers.webhook_router import router as webhook_router
from app.seed import seed_products


@asynccontextmanager
async def lifespan(app: FastAPI):
    stripe.api_key = get_settings().stripe_secret_key
    Base.metadata.create_all(engine)
    with SessionLocal() as session:
        seed_products(session)
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="Order AI Recommendations", lifespan=lifespan)
    app.include_router(webhook_router)
    return app
