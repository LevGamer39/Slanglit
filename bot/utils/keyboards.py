from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
from database import FDataBase

def connect_db():
    return sqlite3.connect('translations.db')

db = FDataBase(connect_db())

def is_user_admin(user_id: int) -> bool:
    admin_role = db.getAdminByLogin(str(user_id))
    return admin_role in ["GreatAdmin", "Admin"]

def get_main_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="🔄 Перевод")],
        [KeyboardButton(text="📖 История"), KeyboardButton(text="📚 Словарь")],
    ]
    if is_user_admin(user_id):
        keyboard.append([KeyboardButton(text="⚙️ Админ-панель")])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_admin_keyboard(admin_role: str) -> ReplyKeyboardMarkup:
    if admin_role == "GreatAdmin":
        keyboard = [
            [KeyboardButton(text="👥 Список админов")],
            [KeyboardButton(text="➕ Добавить админа"), KeyboardButton(text="➖ Удалить админа")],
            [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="📝 Управление словарем")],
            [KeyboardButton(text="⬅️ Назад в меню")]
        ]
    else:
        keyboard = [
            [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="📝 Управление словарем")],
            [KeyboardButton(text="⬅️ Назад в меню")]
        ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

translation_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💼 Неформальный → Формальный")],
        [KeyboardButton(text="🔥 Формальный → Неформальный")],
        [KeyboardButton(text="⬅️ Назад в меню")]
    ],
    resize_keyboard=True
)

translation_mode_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="❌ Выйти из режима перевода")]],
    resize_keyboard=True
)

cancel_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="❌ Отменить")]],
    resize_keyboard=True
)

dictionary_management_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Добавить слово"), KeyboardButton(text="➖ Удалить слово")],
        [KeyboardButton(text="⬅️ Назад в админ-панель")]
    ],
    resize_keyboard=True
)

confirm_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Да, удалить"), KeyboardButton(text="❌ Нет, отменить")],
    ],
    resize_keyboard=True
)

role_selection_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👑 GreatAdmin"), KeyboardButton(text="👤 Admin")],
        [KeyboardButton(text="❌ Отменить")]
    ],
    resize_keyboard=True
)