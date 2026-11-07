import os
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from database import users_collection

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = "9090771899:AAGm3Gh3QdZr-DvHaYdhxoUlLDmhNm55K9Y"
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    
    existing_user = await users_collection.find_one({"user_id": user_id})
    if not existing_user:
        await users_collection.insert_one({
            "user_id": user_id,
            "username": username,
            "balance": 100.0,
            "steam_id": None
        })
    
    webapp_url = os.getenv("WEBAPP_URL", "https://winter-drop-bot.onrender.com")
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❄️ Відкрити Winter Drop", web_app=WebAppInfo(url=webapp_url))]
    ])
    
    await message.answer(
        "👋 **Вітаю у Winter Drop CS2!**\n\n"
        "Тут ти можеш відкривати зимові кейси, крутити рулетку та вибивати скіни.\n"
        "Твій початковий баланс: **100.0 ❄️**\n\n"
        "Тисни кнопку нижче і погнали!",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

async def api_get_user(request):
    user_id = int(request.query.get("user_id", 0))
    user = await users_collection.find_one({"user_id": user_id})
    if not user:
        return web.json_response({"balance": 0.0})
    return web.json_response({"balance": user.get("balance", 0.0)})

async def api_open_case(request):
    data = await request.json()
    user_id = int(data.get("user_id"))
    case_key = data.get("case_key")
    
    prices = {"snow_starter": 5.0, "frost_box": 20.0, "ice_king": 50.0}
    price = prices.get(case_key, 5.0)
    
    user = await users_collection.find_one({"user_id": user_id})
    if not user or user.get("balance", 0) < price:
        return web.json_response({"success": False, "msg": "Недостатньо сніжинок!"})
    
    new_balance = user["balance"] - price
    
    import random
    items = [
        {"name": "P250 | Sand Dune", "rarity": "consumer"},
        {"name": "AK-47 | Safari Mesh", "rarity": "industrial"},
        {"name": "AWP | Asiimov", "rarity": "covert"}
    ]
    won_item = random.choice(items)
    if won_item["rarity"] == "covert":
        new_balance += price * 5
        
    await users_collection.update_one({"user_id": user_id}, {"$set": {"balance": new_balance}})
    
    tape = [random.choice(items) for _ in range(15)]
    tape[9] = won_item
    
    return web.json_response({
        "success": True,
        "new_balance": new_balance,
        "won_item": won_item,
        "tape": tape
    })

async def api_daily(request):
    data = await request.json()
    user_id = int(data.get("user_id"))
    reward = 10.0
    
    user = await users_collection.find_one({"user_id": user_id})
    new_balance = user.get("balance", 0) + reward
    await users_collection.update_one({"user_id": user_id}, {"$set": {"balance": new_balance}})
    
    return web.json_response({"success": True, "reward": reward, "new_balance": new_balance, "msg": "Бонус успішно отримано!"})

async def api_link_steam(request):
    data = await request.json()
    user_id = int(data.get("user_id"))
    steam_id = data.get("steam_id")
    
    await users_collection.update_one({"user_id": user_id}, {"$set": {"steam_id": steam_id}})
    return web.json_response({"success": True, "msg": "Steam ID успішно збережено!"})

async def web_server_runner():
    app = web.Application()
    app.router.add_get('/api/user', api_get_user)
    app.router.add_post('/api/open_case', api_open_case)
    app.router.add_post('/api/daily', api_daily)
    app.router.add_post('/api/link_steam', api_link_steam)
    app.router.add_static('/', path='./webapp', show_index=True)
    return app

async def main():
    port = int(os.environ.get("PORT", 10000))
    app = await web_server_runner()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logging.info(f"Web server started on port {port}")
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
