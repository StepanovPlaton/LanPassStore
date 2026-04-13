from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.order_service import ORDER_STATUSES


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Главное меню — стартовая точка всего интерфейса"""
    builder = InlineKeyboardBuilder()
    builder.button(text="📋 Все заказы", callback_data="menu:orders:1")
    builder.button(text="🔍 Найти заказ", callback_data="menu:search")
    builder.button(text="ℹ️ Помощь",      callback_data="menu:help")
    builder.adjust(2, 1)
    return builder.as_markup()


def orders_list_keyboard(orders: list, page: int = 1, per_page: int = 8) -> InlineKeyboardMarkup:
    """Пагинированный список заказов"""
    builder = InlineKeyboardBuilder()

    start = (page - 1) * per_page
    chunk = orders[start : start + per_page]

    for order in chunk:
        status_icon = ORDER_STATUSES.get(order.get("status", ""), "❓")
        builder.button(
            text=f"#{order['ID']} {order.get('customer_name', 'Клиент')} — {status_icon}",
            callback_data=f"order:detail:{order['ID']}",
        )
    builder.adjust(1)

    total_pages = (len(orders) + per_page - 1) // per_page
    nav = []
    if page > 1:
        nav.append(("◀️", f"menu:orders:{page - 1}"))
    nav.append((f"{page}/{total_pages}", "noop"))
    if page < total_pages:
        nav.append(("▶️", f"menu:orders:{page + 1}"))

    for label, cbd in nav:
        builder.button(text=label, callback_data=cbd)

    builder.adjust(*([1] * len(chunk)), len(nav))
    builder.button(text="🔙 Главное меню", callback_data="menu:main")
    builder.adjust(*([1] * len(chunk)), len(nav), 1)
    return builder.as_markup()


def order_detail_keyboard(order_id: int, back_page: int = 1) -> InlineKeyboardMarkup:
    """Карточка заказа"""
    builder = InlineKeyboardBuilder()
    builder.button(text="🔄 Изменить статус", callback_data=f"order:status_pick:{order_id}")
    builder.button(text="🔙 К списку",        callback_data=f"menu:orders:{back_page}")
    builder.adjust(1)
    return builder.as_markup()


def status_pick_keyboard(order_id: int) -> InlineKeyboardMarkup:
    """Выбор нового статуса"""
    builder = InlineKeyboardBuilder()
    for key, label in ORDER_STATUSES.items():
        builder.button(text=label, callback_data=f"order:set_status:{order_id}:{key}")
    builder.button(text="🔙 Назад", callback_data=f"order:detail:{order_id}")
    builder.adjust(2)
    return builder.as_markup()