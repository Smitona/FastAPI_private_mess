import uuid
import datetime as dt
from bson.objectid import ObjectId

from fastapi import Query

from pydantic import (
    BaseModel, EmailStr, field_validator, Field
)
from typing import Annotated, Optional

import database


class ObjectIdStr(str):
    class Config:
        json_encoders = {ObjectId: lambda oid: str(oid)}


class User(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias='_id')
    username: str = Field(examples=['dimaivanov'])
    first_name: str = Field(examples=['Dima'])
    last_name: str = Field(examples=['Ivanov'])
    email: EmailStr | None = Field(default=None)
    password: str = Field(examples=['password'])
    number: Optional[str] | None = Field(examples=['+79236742401'])
    image: Optional[str] | None = Field(default=None)

    @field_validator('username')
    def unique_username(username):
        if database.users.find_one({"username": username}):
            raise ValueError('User with this username already registered!')
        return username

    @field_validator('email')
    def unique_email(email):
        if database.users.find_one({"email": email}):
            raise ValueError('User with this email already registered!')
        return email

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: lambda oid: str(oid)}


class UserUpdate(BaseModel):
    first_name: str = Field(examples=['Dima'])
    last_name: str = Field(examples=['Ivanov'])
    email: EmailStr | None = Field(default=None)
    password: str = Field(examples=['password'])
    number: Optional[str] | None = Field(examples=['+79236742401'])
    image: Optional[str] | None = Field(default=None)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class Send_message(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias='_id')
    sent_to: str = Field(examples=['dimaivanov'])
    message: Annotated[str, Query(max_length=225)] = Field(
        examples=['Hello']
    )
    sent_at: dt.datetime = dt.datetime.now()

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: lambda oid: str(oid)}


class Message(BaseModel):
    sent_from: str | None
    sent_to: str = Field(examples=['dimaivanov'])
    message: Annotated[str, Query(max_length=225)] = Field(
        examples=['Hello']
    )
    sent_at: dt.datetime = dt.datetime.now()
