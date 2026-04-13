from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.exceptions import TelegramBadRequest

from api import OrderAPI
from keyboards.inline import (
    main_menu_keyboard,
    orders_list_keyboard,
    order_detail_keyboard,
    status_pick_keyboard,
)
from keyboards.reply import force_reply_keyboard
from services.order_service import format_order, ORDER_STATUSES
import logging

logger = logging.getLogger(__name__)

class OrderFSM(StatesGroup):
    waiting_search_id = State()


def _safe_edit(call: types.CallbackQuery, text: str, markup, parse_mode="HTML"):
    """Редактируем текущее сообщение, не отправляем новое."""
    return call.message.edit_text(text, parse_mode=parse_mode, reply_markup=markup)


async def cb_main_menu(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await _safe_edit(call, "👋 <b>Панель управления заказами</b>\n\nВыберите действие:", main_menu_keyboard())
    await call.answer()


async def cb_orders_list(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    page = int(call.data.split(":")[2])
    api = OrderAPI()
    try:
        async with api:
            orders = await api.get_orders()

        if not orders:
            await _safe_edit(call, "📭 Заказов пока нет.", main_menu_keyboard())
        else:
            text = f"📋 <b>Заказы</b> — всего {len(orders)} шт.\nВыберите заказ:"
            await _safe_edit(call, text, orders_list_keyboard(orders, page=page))

    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            pass
        else:
            logger.exception(f"Telegram ошибка: {e}")
            await call.answer("⚠️ Ошибка Telegram", show_alert=True)
    except Exception as e:
        logger.exception(f"Ошибка в cb_orders_list: {e}")
        await call.answer("⚠️ Ошибка загрузки заказов", show_alert=True)
        return

    await call.answer()


async def cb_order_detail(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    order_id = int(call.data.split(":")[2])
    api = OrderAPI()
    try:
        async with api:
            order = await api.get_order_by_id(order_id)
        await _safe_edit(call, format_order(order), order_detail_keyboard(order_id))
    except Exception:
        await call.answer("⚠️ Заказ не найден", show_alert=True)
    await call.answer()


async def cb_status_pick(call: types.CallbackQuery):
    order_id = int(call.data.split(":")[2])
    await _safe_edit(
        call,
        f"🔄 <b>Выберите новый статус</b> для заказа <b>#{order_id}</b>:",
        status_pick_keyboard(order_id),
    )
    await call.answer()


async def cb_set_status(call: types.CallbackQuery):
    _, _, order_id_str, new_status = call.data.split(":")
    order_id = int(order_id_str)
    api = OrderAPI()
    try:
        async with api:
            await api.update_order_status(order_id, new_status)
        label = ORDER_STATUSES.get(new_status, new_status)
        await call.answer(f"✅ Статус → {label}", show_alert=False)
        async with api:
            order = await api.get_order_by_id(order_id)
        await _safe_edit(call, format_order(order), order_detail_keyboard(order_id))
    except Exception:
        await call.answer("⚠️ Ошибка при изменении статуса", show_alert=True)


async def cb_search(call: types.CallbackQuery, state: FSMContext):
    """Запрашиваем ID через ForceReply — чистый ввод без лишних клавиатур"""
    await state.set_state(OrderFSM.waiting_search_id)
    await call.message.answer(
        "🔍 Введите <b>ID заказа</b>:",
        parse_mode="HTML",
        reply_markup=force_reply_keyboard(),
    )
    await call.answer()


async def msg_search_id(message: types.Message, state: FSMContext):
    await state.clear()
    try:
        order_id = int(message.text.strip())
    except ValueError:
        await message.reply("❌ Введите числовой ID.", reply_markup=main_menu_keyboard())
        return

    api = OrderAPI()
    try:
        async with api:
            order = await api.get_order_by_id(order_id)
        await message.answer(
            format_order(order),
            parse_mode="HTML",
            reply_markup=order_detail_keyboard(order_id),
        )
    except Exception:
        await message.reply("⚠️ Заказ не найден.", reply_markup=main_menu_keyboard())


async def cb_help(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    text = (
        "📖 <b>Справка</b>\n\n"
        "📋 <b>Все заказы</b> — список с пагинацией\n"
        "🔍 <b>Найти заказ</b> — поиск по ID\n"
        "🔄 <b>Изменить статус</b> — прямо из карточки заказа\n\n"
        "Всё управление — через кнопки без команд."
    )
    await _safe_edit(call, text, main_menu_keyboard())
    await call.answer()


async def cb_noop(call: types.CallbackQuery):
    await call.answer()


def register_orders_handler(router: Router):
    router.callback_query.register(cb_main_menu,    lambda c: c.data == "menu:main")
    router.callback_query.register(cb_orders_list,  lambda c: c.data.startswith("menu:orders:"))
    router.callback_query.register(cb_search,       lambda c: c.data == "menu:search")
    router.callback_query.register(cb_help,         lambda c: c.data == "menu:help")
    router.callback_query.register(cb_noop,         lambda c: c.data == "noop")
    router.callback_query.register(cb_order_detail, lambda c: c.data.startswith("order:detail:"))
    router.callback_query.register(cb_status_pick,  lambda c: c.data.startswith("order:status_pick:"))
    router.callback_query.register(cb_set_status,   lambda c: c.data.startswith("order:set_status:"))
    router.message.register(msg_search_id, OrderFSM.waiting_search_id)