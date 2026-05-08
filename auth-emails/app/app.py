from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.database import create_tables
from app.exceptions import NotAuthenticated, NotVerified
from app.routers.auth_router import router as auth_router
from app.routers.password_router import router as password_router
from app.routers.verification_router import router as verification_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="Auth Email Demo", lifespan=lifespan)

    @app.exception_handler(NotAuthenticated)
    async def not_authenticated_handler(request, exc):
        return RedirectResponse("/login", status_code=303)

    @app.exception_handler(NotVerified)
    async def not_verified_handler(request, exc):
        return RedirectResponse("/verify-email", status_code=303)

    app.include_router(auth_router)
    app.include_router(verification_router)
    app.include_router(password_router)

    return app
