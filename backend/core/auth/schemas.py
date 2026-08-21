from datetime import datetime

from ninja import Schema
from pydantic import EmailStr, Field


class RegisterSchema(Schema):
    email: EmailStr
    password: str = Field(min_length=8)
    first_name: str = ""
    last_name: str = ""
    phone_number: str = Field(min_length=8, max_length=20)


class LoginSchema(Schema):
    email: EmailStr
    password: str


class GoogleAuthSchema(Schema):
    id_token: str


class StatusVisibilitySchema(Schema):
    is_status_searchable: bool


class UserSchema(Schema):
    id: int
    email: str
    first_name: str
    last_name: str
    phone_number: str
    auth_provider: str
    subscription_end_date: datetime | None = None
    alliance_badge_enabled: bool = False
    is_status_searchable: bool = False
    email_verified: bool = False
    phone_verified: bool = False
    is_fully_verified: bool = False
    has_alliance_vip: bool = False


class TokenResponse(Schema):
    access_token: str
    token_type: str = "bearer"
    user: UserSchema


class PhoneUpdateSchema(Schema):
    phone_number: str = Field(min_length=8, max_length=20)


class PhoneOtpVerifySchema(Schema):
    code: str


class VerificationMessageSchema(Schema):
    message: str
