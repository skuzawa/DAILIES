#MongoDBと連携するための処理
from decouple import config
from typing import Union
from fastapi import HTTPException
import motor.motor_asyncio
from bson import ObjectId
from auth_utils import AuthJwtCsrf
import asyncio 

MONGO_API_KEY = config("MONGO_API_KEY")

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_API_KEY)
client.get_io_loop = asyncio.get_event_loop

database = client.weight
collection_daily = database.daily
collection_user = database.user
auth = AuthJwtCsrf()

def daily_serializer(daily) -> dict:
    return {
        "id": str(daily["_id"]),
        "date": daily["date"],
        "weight": daily["weight"]
    }

def user_serializer(user) -> dict:
    return {
        "id": str(user["_id"]),
        "email": user["email"],
    }

async def db_create_daily(data: dict) -> Union[dict,bool]: #(引数)->返り値
    #awaitして同期化して値が返ってくるのを待つ
    daily = await collection_daily.insert_one(data)
    new_daily = await collection_daily.find_one({"_id":daily.inserted_id})
    if new_daily:
        return daily_serializer(data)
    return False

async def db_get_daily() -> list:
    dailies = []
    for daily in await collection_daily.find().to_list(length=100):
        dailies.append(daily_serializer(daily))
    return dailies

async def db_get_single_daily(id:str) -> Union[dict,bool]:
    daily = await collection_daily.find_one({"_id":ObjectId(id)})
    if daily:
        return daily_serializer(daily)
    return False

async def db_update_daily(id:str,data:dict) -> Union[dict,bool]:
    daily = await collection_daily.find_one({"_id":ObjectId(id)})
    if daily:
        update_daily = await collection_daily.update_one(
            {"_id":ObjectId(id)},{"$set":data}
        )
        if (update_daily.modified_count > 0):
            new_daily = await collection_daily.find_one({"_id": ObjectId(id)})
            return daily_serializer(new_daily)
    return False

async def db_delete_daily(id:str) -> bool:
    todo = await collection_daily.find_one({"_id":ObjectId(id)})
    if todo:
        db_delete_daily = await collection_daily.delete_one({"_id":ObjectId(id)})
        if(db_delete_daily.deleted_count > 0):
            return True
    return False

async def db_signup(data: dict) -> dict:
    email = data.get("email")
    password = data.get("password")
    overlap_user = await collection_user.find_one({"email": email})
    if overlap_user:
        raise HTTPException(status_code=400, detail='Email is already taken')
    if not password or len(password) < 6:
        raise HTTPException(status_code=400, detail='Password too short')
    user = await collection_user.insert_one({"email": email, "password": auth.generate_hashed_pw(password)})
    new_user = await collection_user.find_one({"_id": user.inserted_id})
    return user_serializer(new_user)


async def db_login(data: dict) -> str:
    email = data.get("email")
    password = data.get("password")
    user = await collection_user.find_one({"email": email})
    if not user or not auth.verify_pw(password, user["password"]):
        raise HTTPException(
            status_code=401, detail='Invalid email or password')
    token = auth.encode_jwt(user['email'])
    return token
