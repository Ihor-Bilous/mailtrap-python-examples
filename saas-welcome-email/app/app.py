from fastapi import FastAPI

from app.routers.signup_router import router as signup_router


def create_app() -> FastAPI:
    app = FastAPI(title="SaaS Welcome Email")
    app.include_router(signup_router)
    return app
