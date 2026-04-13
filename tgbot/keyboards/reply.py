from aiogram.types import ReplyKeyboardMarkup, ForceReply
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def start_keyboard() -> ReplyKeyboardMarkup:
    """Единственная Reply-клавиатура — только на /start"""
    builder = ReplyKeyboardBuilder()
    builder.button(text="📋 Открыть меню заказов")
    return builder.as_markup(resize_keyboard=True)


def force_reply_keyboard(placeholder: str = "Введите ID заказа...") -> ForceReply:
    """ForceReply для ввода ID — чистый UX без лишних кнопок"""
    return ForceReply(selective=True, input_field_placeholder=placeholder)