from fastapi import FastAPI

from app.routers.contact_router import router as contact_router


def create_app() -> FastAPI:
    app = FastAPI(title="AI Contact Form")
    app.include_router(contact_router)
    return app
