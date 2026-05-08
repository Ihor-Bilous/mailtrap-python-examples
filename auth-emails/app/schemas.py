from pydantic import BaseModel, EmailStr, Field


class RegisterSchema(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)


class LoginSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class ForgotPasswordSchema(BaseModel):
    email: EmailStr


class ResendVerificationSchema(BaseModel):
    email: EmailStr


class ResetPasswordSchema(BaseModel):
    token: str
    password: str = Field(min_length=8, max_length=72)
    password_confirm: str
