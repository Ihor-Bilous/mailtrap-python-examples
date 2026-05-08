from fastapi import APIRouter, BackgroundTasks, Depends, Request
from fastapi.responses import RedirectResponse
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.dependencies import MailerDep, get_db, require_verified_user
from app.exceptions import EmailAlreadyRegistered, InvalidCredentials
from app.models import User
from app.schemas import LoginSchema, RegisterSchema
from app.services.auth import clear_session_cookie, set_session_cookie
from app.templates import templates
from app.use_cases.login_user import login_user
from app.use_cases.register_user import register_user
from app.utils import field_errors

router = APIRouter()


@router.get("/")
def root():
    return RedirectResponse("/dashboard", status_code=303)


@router.get("/register")
def register_form(request: Request):
    return templates.TemplateResponse(request, "pages/register.html", {"field_errors": {}, "values": {}})


@router.post("/register")
async def register_post(
    request: Request,
    background_tasks: BackgroundTasks,
    mailer: MailerDep,
    db: Session = Depends(get_db),
):
    raw = dict(await request.form())
    try:
        form = RegisterSchema.model_validate(raw)
    except ValidationError as e:
        return templates.TemplateResponse(request, "pages/register.html", {"field_errors": field_errors(e), "values": raw})

    try:
        user, verification_url = register_user(form.name, form.email, form.password, db)
    except EmailAlreadyRegistered:
        return templates.TemplateResponse(
            request, "pages/register.html",
            {"field_errors": {"email": "An account with this email already exists."}, "values": raw},
        )

    background_tasks.add_task(mailer.send_verification_email, user.name, user.email, verification_url)
    return RedirectResponse(f"/verify-email?email={form.email}", status_code=303)


@router.get("/login")
def login_form(request: Request):
    reset = request.query_params.get("reset")
    success = "Password updated successfully. Please log in." if reset else None
    return templates.TemplateResponse(request, "pages/login.html", {"success": success, "field_errors": {}, "values": {}})


@router.post("/login")
async def login_post(request: Request, db: Session = Depends(get_db)):
    raw = dict(await request.form())
    try:
        form = LoginSchema.model_validate(raw)
    except ValidationError as e:
        return templates.TemplateResponse(request, "pages/login.html", {"field_errors": field_errors(e), "values": raw})

    try:
        user_id = login_user(form.email, form.password, db)
    except InvalidCredentials:
        return templates.TemplateResponse(
            request, "pages/login.html",
            {"error": "Invalid email or password.", "field_errors": {}, "values": raw},
        )

    response = RedirectResponse("/dashboard", status_code=303)
    set_session_cookie(response, user_id)
    return response


@router.post("/logout")
def logout():
    response = RedirectResponse("/login", status_code=303)
    clear_session_cookie(response)
    return response


@router.get("/dashboard")
def dashboard(request: Request, user: User = Depends(require_verified_user)):
    return templates.TemplateResponse(request, "pages/dashboard.html", {"user": user})
