from fastapi import FastAPI, APIRouter, Body, Depends
from fastapi.encoders import jsonable_encoder

from typing import Annotated, List, Optional


from models import User, UserUpdate, Send_message, Message
import auth
import database


router = APIRouter()

app = FastAPI()
app.include_router(auth.router)


@router.get('/')
async def get_users(
    token: Annotated[str, Depends(auth.oauth2_bearer)],
    search: Optional[str] = None
):
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


@router.get('/{user_username}/', response_model=Message)
def get_messages(
    token: Annotated[str, Depends(auth.oauth2_bearer)],
    current_user: Annotated[User, Depends(auth.get_current_user)],
    user_username: str,
):
    user = database.users.find_one(
        {"username": user_username}
    )
    messages = database.messages.find(
        {
            "sent_to": user_username,
            "sent_from": current_user,
        }
    )
    messages = list(messages)

    for message in messages:
        message["_id"] = str(message["_id"])

    return messages


@router.post('/{user_username}/', response_model=Message)
async def message_user(
    token: Annotated[str, Depends(auth.oauth2_bearer)],
    current_user: Annotated[User, Depends(auth.get_current_user)],
    user_username: str,
    message: str
):
    user = database.users.find_one({"username": user_username})
    if user is None:
        raise ValueError("User do not exist! You can't sent message")

    data: dict = {
        "sent_from": current_user['username'],
        "sent_to": user_username,
        "message": message
    }
    new_message = database.messages.insert_one(data)
    sent_message = database.messages.find_one(
        {"_id": new_message.inserted_id}
    )

    return sent_message


@router.get('/me/', response_model=User)
def get_user_me(
    current_user: Annotated[User, Depends(auth.get_current_user)]
):
    return current_user


@router.put('/me', response_model=User)
def update_user(
    data: UserUpdate,
    current_user: Annotated[User, Depends(auth.get_current_user)]
):
    changes = {k: v for k, v in data.model_dump().items() if v is not None}
    database.users.update_one(
        {"username": current_user.username}, {"$set": changes}
    )

    updated_user = database.users.find_one({"username": current_user.username})
    if changes.modified_count == 1:
        return updated_user

    return {
        "message": f"Error occured while updating profile {data.name}"
    }


app.include_router(router, tags=['Users'], prefix='/api/users')
