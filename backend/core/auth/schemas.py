from datetime import datetime

from ninja import Schema
from pydantic import EmailStr, Field


class RegisterSchema(Schema):
    email: EmailStr
    password: str = Field(min_length=8)
    first_name: str = ""
    last_name: str = ""


class LoginSchema(Schema):
    email: EmailStr
    password: str


class GoogleAuthSchema(Schema):
    id_token: str


class UserSchema(Schema):
    id: int
    email: str
    first_name: str
    last_name: str
    auth_provider: str
    subscription_end_date: datetime | None = None


class TokenResponse(Schema):
    access_token: str
    token_type: str = "bearer"
    user: UserSchema
