from aiohttp import web
from aiogram import Bot
from config import config
from services.order_service import format_order
from keyboards.inline import order_detail_keyboard

bot = Bot(token=config.BOT_TOKEN)


async def send_order_notification(order: dict) -> None:
    """Отправка уведомления о новом заказе с inline-кнопками"""
    order_id = order.get("ID")
    text = f"🆕 <b>Новый заказ!</b>\n\n{format_order(order)}"

    for chat_id in config.CHAT_ID_LIST:
        if not chat_id:
            continue
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode="HTML",
                reply_markup=order_detail_keyboard(order_id) if order_id else None,
            )
        except Exception as e:
            import logging
            logging.error(f"Ошибка отправки в {chat_id}: {e}")


async def handle_webhook(request: web.Request) -> web.Response:
    """Обработчик webhook от бэкенда"""
    if request.headers.get("X-Webhook-Secret") != config.SECRET:
        return web.Response(status=401, text="Unauthorized")
    try:
        data = await request.json()
        await send_order_notification(data)
        return web.Response(text="OK")
    except Exception as e:
        import logging
        logging.error(f"Ошибка webhook: {e}")
        return web.Response(status=500, text="Error")


async def start_webhook_server() -> web.AppRunner:
    """Запуск webhook сервера"""
    app = web.Application()
    app.router.add_post("/webhook/order", handle_webhook)

    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", 8888).start()

    import logging
    logging.info("Webhook сервер запущен на :8888")
    return runner