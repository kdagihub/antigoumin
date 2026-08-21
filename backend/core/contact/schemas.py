from ninja import Schema
from pydantic import EmailStr, Field


class ContactCreateSchema(Schema):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    destination: str = "contact"
    message: str = Field(min_length=10, max_length=4000)
    website: str = ""


class ContactResultSchema(Schema):
    message: str
