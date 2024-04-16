import datetime as dt
from bson.objectid import ObjectId

from fastapi import Query

from pydantic import BaseModel, EmailStr, Field
from typing import Annotated, Optional


class User(BaseModel):
    id: Optional[str] = Field(alias='_id')
    username: str = Field(examples=['dimaivanov'])
    first_name: str = Field(examples=['Dima'])
    last_name: str = Field(examples=['Ivanov'])
    email: EmailStr | None = Field(default=None)
    password: str = Field(examples=['password'])
    number: Optional[str] | None = Field(examples=['+79236742401'])
    image: Optional[str] | None = Field(default=None)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: lambda oid: str(oid)}


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class Sent_message(BaseModel):
    id: Optional[str] = Field(alias='_id')
    sent_from: User
    sent_to: User
    message: Annotated[str, Query(max_length=225)] = Field(
        examples=['Hello']
    )
    sent_at: dt.datetime = dt.datetime.now()

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: lambda oid: str(oid)}

