import os
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from motor.motor_asyncio import AsyncIOMotorClient

# Налаштування логування
logging.basicConfig(level=logging.INFO)

# Токен твого бота та налаштування
BOT_TOKEN = "9090771899:AAHHUdTfGqDZ2S-LIcQNeGxZWE0fGjlhCI"
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("Помилка: не знайдено змінну середовища MONGO_URI!")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Підключення до MongoDB
db_client = AsyncIOMotorClient(MONGO_URI)
db = db_client.winter_drop_db
users_collection = db.users

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "❄️ Привет! Добро пожаловать в **Winter Drop**.\n\nНажми кнопку **Open** в левом нижнем углу или открой мини-приложение, чтобы начать открывать кейсы!",
        parse_mode="Markdown"
    )

# Обробник для віддачі головної сторінки WebApp
async def index_handler(request):
    return web.FileResponse('./webapp/index.html')

async def web_server_runner():
    app = web.Application()
    
    # Головний маршрут для відкриття веб-додатка
    app.router.add_get('/', index_handler)
    
    # Статичні файли (CSS, JS тощо)
    app.router.add_static('/', path='./webapp', show_index=False)
    
    return app

async def main():
    # Запуск вебсервера для Render на порті 10000
    app = await web_server_runner()
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logging.info(f"Web server started on port {port}")

    # Запуск Telegram бота (polling)
    logging.info("Start polling")
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
