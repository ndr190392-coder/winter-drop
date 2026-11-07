import asyncio
import time
import random
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web
import database as db

API_TOKEN = "9090771899:AAGm3Gh3QdZr-DvHaYdhxoUlLDmhNm55K9Y"
ADMIN_IDS = [9090771899, 123456789] # Твій Telegram ID

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- Конфігурація кейсів та drop-rate ---
CASES = {
    "snow_starter": {
        "name": "❄️ Снежный Старт",
        "price": 5.0,
        "items": [
            {"id": 1, "name": "P250 | Sand Dune", "rarity": "consumer", "price": 4.8, "weight": 40},
            {"id": 2, "name": "AK-47 | Safari Mesh", "rarity": "industrial", "price": 5.2, "weight": 40},
            {"id": 3, "name": "Glock-18 | Winter Camo", "rarity": "industrial", "price": 5.5, "weight": 20},
            {"id": 99, "name": "★ Karambit | Fade", "rarity": "covert", "price": 500.0, "weight": 0}
        ]
    },
    "frost_box": {
        "name": "☃️ Морозный Сундук",
        "price": 20.0,
        "items": [
            {"id": 4, "name": "MP9 | Storm", "rarity": "consumer", "price": 4.0, "weight": 50},
            {"id": 5, "name": "Nova | Polar Mesh", "rarity": "consumer", "price": 5.0, "weight": 35},
            {"id": 6, "name": "M4A4 | Urban DDPAT", "rarity": "industrial", "price": 7.0, "weight": 15},
            {"id": 99, "name": "★ Butterfly Knife", "rarity": "covert", "price": 800.0, "weight": 0}
        ]
    },
    "ice_king": {
        "name": "🧊 Ледяной Дракон",
        "price": 50.0,
        "items": [
            {"id": 7, "name": "P90 | Ash Wood", "rarity": "consumer", "price": 6.0, "weight": 60},
            {"id": 8, "name": "USP-S | Forest Leaves", "rarity": "industrial", "price": 10.0, "weight": 30},
            {"id": 9, "name": "AWP | Pit Viper (BS)", "rarity": "restricted", "price": 15.0, "weight": 10},
            {"id": 99, "name": "AWP | Dragon Lore", "rarity": "covert", "price": 2000.0, "weight": 0}
        ]
    }
}

# --- Обробники Telegram Бота ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await db.get_user(message.from_user.id)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❄️ Открыть Winter Drop App", web_app=WebAppInfo(url="https://your-domain.com/webapp/index.html"))],
        [InlineKeyboardButton(text="📜 Правила проекта", callback_data="rules")]
    ])
    text = (
        "❄️ **Добро пожаловать в WINTER DROP CS2!** ❄️\n\n"
        "Испытай удачу в нашем зимнем дропе! Самые честные кейсы, ежедневные бонусы и крутые скинчики.\n\n"
        "👇 Нажми кнопку ниже, чтобы открыть Mini App!"
    )
    await message.answer(text, parse_mode="Markdown", reply_markup=kb)

@dp.callback_query(F.data == "rules")
async def show_rules(call: types.CallbackQuery):
    rules = (
        "❄️ **ПРАВИЛА ПРОЕКТА WINTER DROP** ❄️\n\n"
        "1. ⛔ **Мультиаккаунты запрещены!** Создание более одного аккаунта влечет вечный бан всех профилей.\n"
        "2. 🔗 **Привязка Steam:** Один Steam ID можно привязать только к ОДНОМУ Telegram-аккаунту.\n"
        "3. 🤝 **Вывод скинов:** Заявки обрабатываются в течение 24 часов.\n"
        "4. 🛡️ Попытка абуза системы приведёт к обнулению баланса."
    )
    await call.message.answer(rules, parse_mode="Markdown")

# --- Адмін Панель ---
@dp.message(Command("admin"))
async def cmd_admin(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    text = (
        "👑 **АДМИН ПАНЕЛЬ** 👑\n\n"
        "Команды админа:\n"
        "`/give <tg_id> <amount>` - Начислить баланс\n"
        "`/ban <tg_id>` - Заблокировать юзера\n"
        "`/stats` - Статистика экономики"
    )
    await message.answer(text, parse_mode="Markdown")

@dp.message(Command("give"))
async def cmd_give(message: types.Message):
    if message.from_user.id not in ADMIN_IDS: return
    args = message.text.split()
    if len(args) < 3: return await message.answer("Используй: /give <tg_id> <amount>")
    target_id, amount = int(args[1]), float(args[2])
    usr = await db.get_user(target_id)
    usr["balance"] += amount
    await db.update_user(target_id, usr)
    await message.answer(f"✅ Успешно! Баланс {target_id} пополнен на {amount}❄️")

# --- WebApp HTTP Server (API) ---
async def handle_get_user(request):
    user_id = request.query.get("user_id")
    if not user_id: return web.json_response({"error": "No user_id"}, status=400)
    data = await db.get_user(int(user_id))
    return web.json_response(data)

async def handle_daily(request):
    body = await request.json()
    user_id = body.get("user_id")
    usr = await db.get_user(int(user_id))
    
    now = time.time()
    if now - usr.get("last_daily", 0) < 86400:
        return web.json_response({"success": False, "msg": "Кулдаун 24 часа! Зайди позже."})
    
    reward = random.randint(2, 5)
    usr["balance"] += reward
    usr["last_daily"] = now
    await db.update_user(int(user_id), usr)
    return web.json_response({"success": True, "reward": reward, "new_balance": usr["balance"]})

async def handle_link_steam(request):
    body = await request.json()
    user_id, steam_id = body.get("user_id"), body.get("steam_id")
    if await db.is_steam_linked(steam_id, int(user_id)):
        return web.json_response({"success": False, "msg": "Этот Steam ID уже привязан к другому аккаунту!"})
    await db.link_steam(steam_id, int(user_id))
    return web.json_response({"success": True, "msg": "Steam успешно привязан!"})

async def handle_open_case(request):
    body = await request.json()
    user_id, case_key = body.get("user_id"), body.get("case_key")
    if case_key not in CASES: return web.json_response({"error": "Invalid case"}, status=400)
    
    case_info = CASES[case_key]
    usr = await db.get_user(int(user_id))
    
    if usr["balance"] < case_info["price"]:
        return web.json_response({"success": False, "msg": "Недостаточно средств!"})
    
    usr["balance"] -= case_info["price"]
    
    items = case_info["items"]
    weights = [i["weight"] for i in items]
    won_item = random.choices(items, weights=weights, k=1)[0]
    
    usr["inventory"].append(won_item)
    await db.update_user(int(user_id), usr)
    
    roulette_tape = []
    possible_fillers = [i for i in items if i["weight"] > 0]
    for _ in range(25):
        roulette_tape.append(random.choice(possible_fillers))
    
    roulette_tape.append(items[-1]) 
    roulette_tape.append(won_item)  
    
    for _ in range(5):
        roulette_tape.append(random.choice(possible_fillers))

    return web.json_response({
        "success": True,
        "won_item": won_item,
        "tape": roulette_tape,
        "new_balance": usr["balance"]
    })

async def main():
    app = web.Application()
    app.router.add_get("/api/user", handle_get_user)
    app.router.add_post("/api/daily", handle_daily)
    app.router.add_post("/api/link_steam", handle_link_steam)
    app.router.add_post("/api/open_case", handle_open_case)
    app.router.add_static("/webapp/", path="webapp", name="webapp")
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    asyncio.create_task(site.start())
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())