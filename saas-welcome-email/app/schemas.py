from pydantic import BaseModel, EmailStr, Field, field_validator

_ROLES = {"developer", "founder", "marketer", "designer", "product_manager", "other"}
_COMPANY_SIZES = {"solo", "2-10", "11-50", "51-200", "200+"}


class SignupFormSchema(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr
    role: str
    company_size: str = "solo"
    use_case: str = Field(..., min_length=1, max_length=1000)

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        if v not in _ROLES:
            raise ValueError("Select a valid role")
        return v

    @field_validator("company_size")
    @classmethod
    def validate_company_size(cls, v: str) -> str:
        if v not in _COMPANY_SIZES:
            raise ValueError("Select a valid company size")
        return v
