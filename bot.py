import os
import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from motor.motor_asyncio import AsyncIOMotorClient

# Налаштування логування
logging.basicConfig(level=logging.INFO)

# Отримуємо змінні середовища з Render
BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")

if not BOT_TOKEN:
    raise ValueError("Помилка: не знайдено змінну середовища BOT_TOKEN!")

if not MONGO_URI:
    raise ValueError("Помилка: не знайдено змінну середовища MONGO_URI!")

# Ініціалізація бота, диспетчера та бази даних MongoDB
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

db_client = AsyncIOMotorClient(MONGO_URI)
db = db_client.winter_drop  # Назва твоєї бази даних

# Обробник команди /start російською мовою
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "❄️ Добро пожаловать в Winter Drop!\n\n"
        "Жми на кнопку ниже, чтобы открыть мини-приложение и испытать удачу!"
    )

# Простий вебсервер для Render (щоб порт 10000 був зайнятий і сервіс не відключався)
async def index_handler(request):
    return web.FileResponse('./index.html')

async def web_server():
    app = web.Application()
    app.router.add_get('/', index_handler)
    # Статичні файли (якщо є папка static)
    if os.path.exists('static'):
        app.router.add_static('/static/', path='static', show_index=False)
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Render передає порт через змінну PORT, за замовчуванням 10000
    port = int(os.getenv("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logging.info(f"Web server started on port {port}")

async def main():
    # Запускаємо вебсервер у фоновому режимі
    asyncio.create_task(web_server())
    
    # Запускаємо поллінг бота
    logging.info("Start polling")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
