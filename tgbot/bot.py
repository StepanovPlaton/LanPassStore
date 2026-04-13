import asyncio
import logging
from aiogram import Bot, Dispatcher

from config import config
from handlers import register_handlers
from webhook import start_webhook_server

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


async def main():
    """Точка входа в бота"""
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()

    register_handlers(dp)

    webhook_runner = await start_webhook_server()
    
    try:
        await dp.start_polling(bot)
    finally:
        await webhook_runner.cleanup()
        await bot.close()


if __name__ == "__main__":
    asyncio.run(main())