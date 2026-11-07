import os
from motor.motor_asyncio import AsyncIOMotorClient

# Рядок підключення до тєї хмарної бази MongoDB Atlas
MONGO_URL = os.getenv("MONGO_URI", "mongodb+srv://ndr190392_db_user:510SqIvxrAVWsWfo@cluster0.meedhth.mongodb.net/")

client = AsyncIOMotorClient(MONGO_URL)
db = client["winter_drop"]

users_collection = db["users"]
steam_collection = db["steam_links"]

async def get_user(user_id: int):
    user = await users_collection.find_one({"user_id": user_id})
    if not user:
        user = {
            "user_id": user_id,
            "balance": 10.0,
            "streak": 0,
            "last_daily": 0,
            "steam_id": None,
            "inventory": [],
            "banned": False
        }
        await users_collection.insert_one(user)
    else:
        user.pop("_id", None)
    return user

async def update_user(user_id: int, data: dict):
    await users_collection.update_one(
        {"user_id": user_id},
        {"$set": data},
        upsert=True
    )

async def is_steam_linked(steam_id: str, user_id: int) -> bool:
    link = await steam_collection.find_one({"steam_id": steam_id})
    if link and link["user_id"] != user_id:
        return True
    return False

async def link_steam(steam_id: str, user_id: int):
    await steam_collection.update_one(
        {"steam_id": steam_id},
        {"$set": {"user_id": user_id}},
        upsert=True
    )
    await users_collection.update_one(
        {"user_id": user_id},
        {"$set": {"steam_id": steam_id}}
    )