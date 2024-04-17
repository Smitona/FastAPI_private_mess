import datetime as dt
from fastapi import FastAPI, APIRouter, Body, Depends
from fastapi.encoders import jsonable_encoder

from typing import Annotated, Optional


from models import User, UserUpdate, Message
import auth
import database


router = APIRouter()

app = FastAPI()
app.include_router(auth.router)


@router.get('/')
async def get_users(
    token: Annotated[str, Depends(auth.oauth2_bearer)],
    search: Optional[str] = None,
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


@router.get('/{user_username}/')
def get_messages(
    token: Annotated[str, Depends(auth.oauth2_bearer)],
    current_user: Annotated[User, Depends(auth.get_current_user)],
    user_username: str,
):
    """ user = database.users.find_one(
        {"username": user_username}
    )
    if user is None:
        raise ValueError("User do not exist!")"""
    messages_to = list(database.messages.find(
        {
            "sent_to": user_username,
            "sent_from": current_user,
        }
    ))

    messages_from = list(database.messages.find(
        {
            "sent_to": current_user,
            "sent_from": user_username,
        }
    ))

    messages = messages_to + messages_from
    messages = sorted(
        messages,
        key=lambda x: dt.datetime.strptime(
                x['sent_at'], '%Y-%m-%d %H:%M:%S'
            ), reverse=True
        )

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


@router.get('/me/')
def profile(
    token: Annotated[str, Depends(auth.oauth2_bearer)],
    current_user: Annotated[User, Depends(auth.get_current_user)]
):
    user = database.users.find_one(
        {"username": current_user['username']}
    )
    return user


@router.patch('/me', response_model=User)
def update_profile(
    token: Annotated[str, Depends(auth.oauth2_bearer)],
    current_user: Annotated[User, Depends(auth.get_current_user)],
    data: UserUpdate = Body(),
):
    stored_user_data = database.users.find_one(
        {"username": current_user['username']}
    )

    stored_user_model = UserUpdate(**stored_user_data)
    update_data = data.model_dump(exclude_unset=True)

    updated_user = stored_user_model.model_copy(update=update_data)
    updated_user = jsonable_encoder(updated_user)

    updated_data = database.users.update_one(
        {"username": current_user['username']}, {"$set": updated_user}
    )

    if updated_data:
        updated_data = database.users.find_one(
            {"username": current_user['username']}
        )
        return updated_data

    return {
        "message": f"Error occured while updating profile {data.username}"
    }


app.include_router(router, tags=['Users'], prefix='/api/users')
