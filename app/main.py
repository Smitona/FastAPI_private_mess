import datetime as dt
import jwt
import os

from http import HTTPStatus
from pymongo import MongoClient

from fastapi import (
    FastAPI, APIRouter, Body, Depends, Request, HTTPException
    )
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext


from typing_extensions import Annotated
from typing import Annotated, List, Optional


from models import User, ListUser, Sent_message
import database


router = APIRouter()

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

"""
@app.on_event("startup")
def startup_db_client():
    app.mongodb_client = MongoClient(config["MONGODB_CONNECTION_URI"])
    app.database = app.mongodb_client[config["DB_NAME"]]
    print("Connected to the MongoDB database!")

@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()"""


SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
EXPIRATION_TIME = dt.timedelta(minutes=40)


def create_jwt_token(data: dict):
    expiration = dt.datetime.now() + EXPIRATION_TIME
    data.update({"exp": expiration})
    token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_jwt_token(token: str):
    try:
        decoded_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_data
    except jwt.PyJWTError:
        return None


def get_current_user(token: str = Depends(oauth2_scheme)):
    decoded_data = verify_jwt_token(token)
    if not decoded_data:
        raise HTTPException(HTTPStatus.BAD_REQUEST, detail='Invalid token.')
    user = get_user(decoded_data["sub"])
    if not user:
        raise HTTPException(HTTPStatus.BAD_REQUEST, detail='User not found.')
    return user


@router.get('/', response_model=List[ListUser])
async def get_users(token: Annotated[str, Depends(oauth2_scheme)]):
    users = List[User]
    return users


@router.post('/')
async def create_user(request: Request, user: User = Body()):
    user = jsonable_encoder(user)
    new_user = database.users.insert_one(user)
    created_user = database.users.find_one(
        {"_id": new_user.inserted_id}
    )
    return created_user


@router.get('/{user_username}/')
def get_user(
    request: Request, user_username: str,
    current_user: Annotated[User, Depends(get_current_user)]
):
    user = database.users.find_one(
        {"_username": user_username}
    )
    messages = database.messages.find(
        {
            "_sent_to": user,
            "_sent_from": current_user,
        }
    )
    return List[messages]


@router.post('/{user_username}/', response_model=Sent_message)
async def message_user(
    user_username: str,
    token: Annotated[str, Depends(oauth2_scheme)],
    current_user: User = Depends(get_current_user),
    message: Sent_message = Body()
):
    message = jsonable_encoder(message)
    new_message = database.messages.insert_one(message)
    sent_message = database.messages.find_one(
        {"_id": new_message.inserted_id}
    )

    return sent_message

@router.get('/me/')
def get_user_me(current_user: User = Depends(get_current_user)):
    return current_user


app.include_router(router, tags=['Users'], prefix='/api/users')
