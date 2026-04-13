from datetime import datetime
from typing import List, Dict, Any
from config import config


ORDER_STATUSES = {
    "pending":    "⏳ Ожидает",
    "processing": "🔧 В работе",
    "shipped":    "🚚 Отправлен",
    "delivered":  "✅ Доставлен",
    "cancelled":  "❌ Отменён",
}


def format_order_status(status: str) -> str:
    """Форматирование статуса заказа в текст"""
    return config.STATUS_TEXT.get(status, status)


def format_order_items(items: List[Dict[str, Any]]) -> str:
    """Форматирование списка товаров в заказе"""
    if not items:
        return "Товары: отсутствуют"
    
    lines = []
    for i, item in enumerate(items, 1):
        product = item.get("product", {})
        title = product.get("title", "Неизвестный товар")
        price = product.get("price", 0)
        quantity = item.get("quantity", 1)
        
        lines.append(
            f"{i}. {title} - {price} Тг x {quantity} шт."
        )
    
    return "\n".join(lines)


def format_order(order: Dict[str, Any]) -> str:
    """Форматирование заказа для отправки в Telegram"""
    order_id = order.get("ID", "N/A")
    customer_name = order.get("customer_name", "Не указан")
    customer_phone = order.get("customer_phone", "Не указан")
    customer_email = order.get("customer_email", "Не указан")
    total_price = order.get("total_price", 0)
    status = order.get("status", "new")
    comment = order.get("comment", "")
    items = order.get("items", [])
    

    status_text = format_order_status(status)

    items_text = format_order_items(items)

    comment_text = f"Комментарий: {comment}" if comment else "Комментарий: отсутствует"

    order_text = (
        f"📦 <b>Заказ #{order_id}</b>\n"
        f"Статус: {status_text}\n"
        f"\n"
        f"👤 <b>Клиент:</b> {customer_name}\n"
        f"📞 {customer_phone}\n"
        f"✉️ {customer_email}\n"
        f"\n"
        f"💰 <b>Итого:</b> {total_price} Тг\n"
        f"\n"
        f"<b>Товары:</b>\n"
        f"{items_text}\n"
        f"\n"
        f"{comment_text}"
    )
    
    return order_text


def format_order_list(orders: List[Dict[str, Any]]) -> str:
    """Форматирование списка заказов для отображения в Telegram"""
    if not orders:
        return "Заказы отсутствуют."
    
    lines = []
    for order in orders:
        order_id = order.get("ID", "N/A")
        customer_name = order.get("customer_name", "Не указан")
        total_price = order.get("total_price", 0)
        status = order.get("status", "new")
        status_text = format_order_status(status)
        
        lines.append(
            f"#{order_id} {customer_name} - {total_price} Тг [{status_text}]"
        )
    
    return "\n".join(lines)


async def get_orders() -> List[Dict[str, Any]]:
    """Получение списка заказов через API"""
    from api import OrderAPI
    api = OrderAPI()
    async with api:
        return await api.get_orders()
