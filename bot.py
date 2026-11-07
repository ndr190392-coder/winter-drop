import os
import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from motor.motor_asyncio import AsyncIOMotorClient

logging.basicConfig(level=logging.INFO)

# Жорстко прописуємо дані, щоб виключити проблеми зі змінними на Render
BOT_TOKEN = "9090771899:AAHHUdTfGqDZ2S-LIcQNeGxZWE0fGjlhCI"
MONGO_URI = "mongodb+srv://ndr190392_db_user:510SqIvxrAVWsWfo@cluster0.meedhth.mongodb.net/"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

db_client = AsyncIOMotorClient(MONGO_URI)
db = db_client.winter_drop

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "❄️ Добро пожаловать в Winter Drop!\n\n"
        "Жми на кнопку ниже, чтобы открыть мини-приложение и испытать удачу!"
    )

async def index_handler(request):
    return web.FileResponse('./index.html')

async def web_server():
    app = web.Application()
    app.router.add_get('/', index_handler)
    if os.path.exists('static'):
        app.router.add_static('/static/', path='static', show_index=False)
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.getenv("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logging.info(f"Web server started on port {port}")

async def main():
    asyncio.create_task(web_server())
    logging.info("Start polling")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
