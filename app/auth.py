import datetime as dt
import os

from jose import jwt, JWTError

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
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
    print(user)
    if not user:
        raise ValueError('User do not exist. Wrong password or username.')
    return user


def create_jwt_token(
    data: dict,
    expires_delta: dt.timedelta | None = None
):
    to_encode = data.copy()
    if expires_delta:
        expire = dt.datetime.now() + expires_delta
    expire = dt.datetime.now() + dt.timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        data, SECRET_KEY, algorithm=ALGORITHM
    )

    return encoded_jwt


def get_user(db: database.users, username: str):
    user = db.find_one({"username": username})

    return user


async def get_current_user(
    token: Annotated[str, Depends(oauth2_bearer)]
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authorization": "Bearer"},
    )
    try:
        payload: dict = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = get_user(db=database.users, username=token_data.username)

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
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token_expires = dt.timedelta(minutes=40)
    token = create_jwt_token(
        data={"sub": user['username']}, expires_delta=token_expires
    )
    return Token(access_token=token, token_type="bearer")
