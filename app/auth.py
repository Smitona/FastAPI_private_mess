import datetime as dt
import os

from http import HTTPStatus
import jwt

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext

import database
from models import Token, TokenData

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


async def authenticate_user(username: str, password: str, db: database.users):
    user = db.find_one({
        "username": username,
        "password": password
    })
    return user


def create_jwt_token(
    data: dict,
    expires_delta: dt.timedelta | None = None
):
    to_encode = data.copy()
    if expires_delta:
        expire = dt.datetime.now(dt.timezone.utc) + expires_delta
    expire = dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(
    token: str = Annotated[str, Depends(oauth2_bearer)]
):
    credentials_exception = HTTPException(
        status_code=HTTPStatus.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload: dict = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.JWTError:
        raise credentials_exception

    user = database.users.find_one({"username": token_data.username})
    return user


@router.post('/token', response_model=Token)
async def login_for_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    user = await authenticate_user(
        form_data.username, form_data.password, database.users
    )
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token_expires = dt.timedelta(minutes=40)
    token = create_jwt_token(
        data={"sub": user['username']}, expires_delta=token_expires
    )
    return Token(access_token=token, token_type="bearer")