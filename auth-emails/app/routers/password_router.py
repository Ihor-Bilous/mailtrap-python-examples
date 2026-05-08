from fastapi import APIRouter, BackgroundTasks, Depends, Request
from fastapi.responses import RedirectResponse
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.dependencies import MailerDep, get_db
from app.exceptions import TokenExpired, TokenInvalid
from app.schemas import ForgotPasswordSchema, ResetPasswordSchema
from app.templates import templates
from app.use_cases.request_password_reset import request_password_reset
from app.use_cases.reset_password import reset_password
from app.utils import field_errors

router = APIRouter()


@router.get("/forgot-password")
def forgot_password_form(request: Request):
    return templates.TemplateResponse(request, "pages/forgot_password.html", {"field_errors": {}, "values": {}})


@router.post("/forgot-password")
async def forgot_password_post(
    request: Request,
    background_tasks: BackgroundTasks,
    mailer: MailerDep,
    db: Session = Depends(get_db),
):
    raw = dict(await request.form())
    try:
        form = ForgotPasswordSchema.model_validate(raw)
    except ValidationError as e:
        return templates.TemplateResponse(request, "pages/forgot_password.html", {"field_errors": field_errors(e), "values": raw})

    result = request_password_reset(form.email, db)
    if result:
        name, user_email, reset_url = result
        background_tasks.add_task(mailer.send_reset_email, name, user_email, reset_url)

    # always show generic success to prevent email enumeration
    return templates.TemplateResponse(
        request, "pages/forgot_password.html",
        {"success": "If an account exists for that email, a password reset link has been sent.", "field_errors": {}, "values": {}},
    )


@router.get("/reset-password/{token}")
def reset_password_form(token: str, request: Request):
    return templates.TemplateResponse(request, "pages/reset_password.html", {"token": token, "field_errors": {}, "values": {}})


@router.post("/reset-password")
async def reset_password_post(request: Request, db: Session = Depends(get_db)):
    raw = dict(await request.form())
    try:
        form = ResetPasswordSchema.model_validate(raw)
    except ValidationError as e:
        return templates.TemplateResponse(
            request, "pages/reset_password.html",
            {"token": raw.get("token", ""), "field_errors": field_errors(e), "values": raw},
        )

    if form.password != form.password_confirm:
        return templates.TemplateResponse(
            request, "pages/reset_password.html",
            {"token": form.token, "field_errors": {"password_confirm": "Passwords do not match."}, "values": raw},
        )

    try:
        reset_password(form.token, form.password, db)
    except TokenExpired:
        return templates.TemplateResponse(
            request, "pages/reset_password.html",
            {"token": form.token, "error": "This reset link has expired. Please request a new one.", "field_errors": {}, "values": raw},
        )
    except TokenInvalid:
        return templates.TemplateResponse(
            request, "pages/reset_password.html",
            {"token": form.token, "error": "This reset link is invalid.", "field_errors": {}, "values": raw},
        )

    return RedirectResponse("/login?reset=1", status_code=303)
