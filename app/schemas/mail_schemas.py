from pydantic import BaseModel, Field, EmailStr

class ForgotEmail(BaseModel):
    email: EmailStr

class ResetPassword(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")