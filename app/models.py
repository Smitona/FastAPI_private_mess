import datetime as dt
from bson.objectid import ObjectId

from fastapi import Query

from pydantic import BaseModel, EmailStr, Field
from typing import Annotated, Optional


class User(BaseModel):
    username: str = Field(examples=['dimaivanov'])
    first_name: str = Field(examples=['Dima'])
    last_name: str = Field(examples=['Ivanov'])
    email: EmailStr | None = Field(default=None)
    password: str
    number: Optional[str] | None = Field(examples=['+79236742401'])
    image: Optional[str] | None = Field(default=None)


class ListUser(BaseModel):
    username: str
    first_name: str
    last_name: str


class Sent_message(BaseModel):
    sent_from: User
    sent_to: User
    message: Annotated[str, Query(max_length=225)] = Field(
        examples=['Hello']
    )
    sent_at: dt.datetime = dt.datetime.now()


