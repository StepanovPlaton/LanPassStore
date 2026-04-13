from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from keyboards.inline import main_menu_keyboard


WELCOME_TEXT = (
    "👋 <b>Панель управления заказами</b>\n\n"
    "Выберите действие в меню ниже:"
)


async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        WELCOME_TEXT,
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(),
    )


async def btn_open_menu(message: types.Message, state: FSMContext):
    """Reply-кнопка 'Открыть меню заказов'"""
    await state.clear()
    await message.answer(
        WELCOME_TEXT,
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(),
    )


def register_menu_handler(router: Router):
    router.message.register(cmd_start, Command("start"))
    router.message.register(
        btn_open_menu,
        lambda m: m.text == "📋 Открыть меню заказов",
    )