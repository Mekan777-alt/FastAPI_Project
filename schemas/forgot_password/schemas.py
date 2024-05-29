from pydantic import BaseModel, EmailStr


class ForgotPassword(BaseModel):
    email: EmailStr


class EnterCode(BaseModel):
    code: str
    new_password: str
