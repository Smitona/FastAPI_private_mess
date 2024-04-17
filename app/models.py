import uuid
import datetime as dt
from bson.objectid import ObjectId

from fastapi import Query

from pydantic import BaseModel, EmailStr, Field
from typing import Annotated, Optional


class User(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias='_id')
    username: str = Field(examples=['dimaivanov'])
    first_name: str = Field(examples=['Dima'])
    last_name: str = Field(examples=['Ivanov'])
    email: EmailStr | None = Field(default=None)
    password: str = Field(examples=['password'])
    number: Optional[str] | None = Field(
        max_length=12, min_length=12, examples=['+79236742401']
    )
    profile_pic: Optional[str] | None = Field(default='https://clck.ru/3A8oWW')

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: lambda oid: str(oid)}


class UserUpdate(BaseModel):
    first_name: str = Field(examples=['Dima'])
    last_name: str = Field(examples=['Ivanov'])
    email: EmailStr | None = Field(default=None)
    password: str = Field(examples=['password'])
    number: Optional[str] | None = Field(
        default='Unknown', examples=['+79236742401']
    )
    image: Optional[str] | None = Field(default='No image')


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class Message(BaseModel):
    sent_from: str | None
    sent_to: str = Field(examples=['dimaivanov'])
    message: Annotated[str, Query(max_length=225)] = Field(
        examples=['Hello']
    )
    sent_at: dt.datetime = dt.datetime.now()
