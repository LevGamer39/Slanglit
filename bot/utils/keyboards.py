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

# Новые клавиатуры для алфавитной навигации
def get_dictionary_main_keyboard():
    """Главная клавиатура словаря"""
    keyboard = [
        [KeyboardButton(text="🔤 По алфавиту"), KeyboardButton(text="🔍 Поиск в словаре")],
        [KeyboardButton(text="📄 Все слова"), KeyboardButton(text="⬅️ Назад в меню")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_alphabet_keyboard(active_letter: str = None):
    """Клавиатура с буквами алфавита"""
    # Русский алфавит
    alphabet = [
        ['А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ё', 'Ж', 'З'],
        ['И', 'Й', 'К', 'Л', 'М', 'Н', 'О', 'П', 'Р'],
        ['С', 'Т', 'У', 'Ф', 'Х', 'Ц', 'Ч', 'Ш', 'Щ'],
        ['Ъ', 'Ы', 'Ь', 'Э', 'Ю', 'Я', 'ALL']
    ]
    
    keyboard = []
    for row in alphabet:
        keyboard_row = []
        for letter in row:
            if letter == active_letter:
                # Подсвечиваем активную букву
                button_text = f"🔘 {letter}"
            else:
                button_text = letter
            keyboard_row.append(KeyboardButton(text=button_text))
        keyboard.append(keyboard_row)
    
    # Добавляем кнопку назад
    keyboard.append([KeyboardButton(text="⬅️ Назад в словарь")])
    
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_letter_navigation_keyboard(letter: str, offset: int, total_words: int, words_per_page: int = 10):
    """Навигация для слов на конкретную букву"""
    keyboard_buttons = []
    
    # Кнопки навигации
    nav_buttons = []
    if offset > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"letter_{letter}_prev_{offset-words_per_page}"))
    
    # Показать текущую позицию
    current_page = (offset // words_per_page) + 1
    total_pages = (total_words + words_per_page - 1) // words_per_page
    if total_pages > 1:
        nav_buttons.append(InlineKeyboardButton(text=f"{current_page}/{total_pages}", callback_data="current_page"))
    
    if offset + words_per_page < total_words:
        nav_buttons.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"letter_{letter}_next_{offset+words_per_page}"))
    
    if nav_buttons:
        keyboard_buttons.append(nav_buttons)
    
    # Кнопка возврата к алфавиту
    keyboard_buttons.append([InlineKeyboardButton(text="🔙 К алфавиту", callback_data="back_to_alphabet")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)