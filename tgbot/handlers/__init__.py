from aiogram import Router

from .start import register_menu_handler
from .orders import register_orders_handler


def register_handlers(dp):
    router = Router()
    
    register_menu_handler(router)
    register_orders_handler(router)

    dp.include_router(router)
