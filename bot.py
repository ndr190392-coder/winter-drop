import os
import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from motor.motor_asyncio import AsyncIOMotorClient

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = "9090771899:AAGTT3MKobwGS5rc8WkRkToe1SlTd52Egug"
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

# Обробник головної сторінки (тепер бере index.html з папки webapp)
async def index_handler(request):
    return web.FileResponse('./webapp/index.html')

async def web_server():
    app = web.Application()
    app.router.add_get('/', index_handler)
    
    # Роздаємо статику (CSS, JS) із папки webapp
    if os.path.exists('webapp'):
        app.router.add_static('/static/', path='webapp', show_index=False)
    
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
