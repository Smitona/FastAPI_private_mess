from fastapi import FastAPI, APIRouter, Body, Depends
from fastapi.encoders import jsonable_encoder

from typing import Annotated, List, Optional


from models import User, Sent_message
import auth
import database


router = APIRouter()

app = FastAPI()
app.include_router(auth.router)

user_depends = Annotated[User, Depends(auth.get_current_user)]
db_depends = Annotated[str, Depends(auth.oauth2_bearer)]


@router.get('/')
async def get_users(token: db_depends, search: Optional[str] = None):
    users = database.users.find({})

    if search:
        users = database.users.find({
            "username": {'$regex': f'^{search}'}
        })
    users = list(users)
    for user in users:
        user["_id"] = str(user["_id"])

    return users


@router.post('/')
async def create_user(user: User = Body()):
    user = jsonable_encoder(user)
    new_user = database.users.insert_one(user)
    created_user = database.users.find_one(
        {"_id": new_user.inserted_id}
    )
    return created_user


@router.get('/{user_username}/')
def get_messages(
    user_username: str,
    current_user: user_depends
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
    user_username: str, token: db_depends,
    current_user: user_depends, message: str
):
    message = jsonable_encoder(message)
    new_message = database.messages.insert_one(message)
    sent_message = database.messages.find_one(
        {"_id": new_message.inserted_id}
    )

    return sent_message


@router.get('/me/', response_model=User)
def get_user_me(token: db_depends, current_user: user_depends):
    return current_user


app.include_router(router, tags=['Users'], prefix='/api/users')
