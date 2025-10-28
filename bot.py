from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
import sqlite3
from database import FDataBase
from typing import Tuple, Optional
from secret import BOT_TOKEN
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

def connect_db():
    return sqlite3.connect('translations.db')

db = FDataBase(connect_db())
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

#pragma region States
class TranslationStates(StatesGroup):
    waiting_for_informal = State()
    waiting_for_formal = State()

class AddWordStates(StatesGroup):
    waiting_for_informal = State()
    waiting_for_formal = State()
    waiting_for_explanation = State()

class SearchStates(StatesGroup):
    waiting_for_search = State()

class AdminStates(StatesGroup):
    waiting_for_admin_login = State()
    waiting_for_admin_role = State()
    waiting_for_admin_remove = State()

class DeleteWordStates(StatesGroup):
    waiting_for_word_input = State()
    waiting_for_confirmation = State()
#pragma endregion

#pragma region Keyboards
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
        [KeyboardButton(text="🎩 Неформальный → Формальный")],
        [KeyboardButton(text="😎 Формальный → Неформальный")],
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
#pragma endregion

#pragma region Utility Functions
def is_user_admin(user_id: int) -> bool:
    admin_role = db.getAdminByLogin(str(user_id))
    return admin_role in ["GreatAdmin", "Admin"]

def translate_to_formal(text: str, user_id: int = None) -> Tuple[str, Optional[str]]:
    original_text = text
    result = db.get_formal_translation(text.lower())
    if result:
        formal_text, explanation = result
        explanation_text = f"{text} → {formal_text}: {explanation}" if explanation else None
        db.add_translation(text, formal_text, explanation_text, user_id, "to_formal")
        return formal_text, explanation_text
    
    words = text.split()
    formal_parts = []
    explanations = []
    
    i = 0
    while i < len(words):
        found = False
        for length in range(min(3, len(words) - i), 0, -1):
            phrase = ' '.join(words[i:i + length])
            result = db.get_formal_translation(phrase.lower())
            if result:
                formal_phrase, explanation = result
                formal_parts.append(formal_phrase)
                if explanation:
                    explanations.append(f"{phrase} → {formal_phrase}: {explanation}")
                i += length
                found = True
                break
        
        if not found:
            formal_parts.append(words[i])
            i += 1
    
    formal_text = ' '.join(formal_parts)
    explanation_text = '\n'.join(explanations) if explanations else None
    
    db.add_translation(text, formal_text, explanation_text, user_id, "to_formal")
    
    return formal_text, explanation_text

def translate_to_informal(text: str, user_id: int = None) -> Tuple[str, Optional[str]]:
    words = text.split()
    informal_parts = []
    explanations = []
    
    i = 0
    while i < len(words):
        found = False
        for length in range(min(3, len(words) - i), 0, -1):
            phrase = ' '.join(words[i:i + length])
            result = db.get_informal_translation(phrase.lower())
            if result:
                informal_phrase, explanation = result
                informal_parts.append(informal_phrase)
                if explanation:
                    explanations.append(f"{phrase} → {informal_phrase}: {explanation}")
                i += length
                found = True
                break
        
        if not found:
            informal_parts.append(words[i])
            i += 1
    
    informal_text = ' '.join(informal_parts)
    explanation_text = '\n'.join(explanations) if explanations else None
    
    db.add_translation(text, informal_text, explanation_text, user_id, "to_informal")
    
    return informal_text, explanation_text
#pragma endregion

#pragma region Main Menu Handlers
@dp.message(CommandStart())
async def start_command(message: types.Message):
    await message.answer(
        "👋 Привет! Я бот для перевода между формальным и неформальным стилем.\n\n"
        "📝 Используй кнопки для навигации!",
        reply_markup=get_main_keyboard(message.from_user.id)
    )

@dp.message(lambda message: message.text == "⬅️ Назад в меню")
async def go_back_to_main_menu(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Главное меню:",
        reply_markup=get_main_keyboard(message.from_user.id)
    )
#pragma endregion

#pragma region Translation Handlers
@dp.message(lambda message: message.text == "🔄 Перевод")
async def show_translation_options(message: types.Message):
    await message.answer(
        "🔄 Выбери направление перевода:",
        reply_markup=translation_keyboard
    )

@dp.message(lambda message: message.text == "🎩 Неформальный → Формальный")
async def start_formal_translation(message: types.Message, state: FSMContext):
    await state.set_state(TranslationStates.waiting_for_informal)
    await message.answer(
        "✅ Режим: Неформальный → Формальный\n\n"
        "Отправь неформальный текст для перевода:\n"
        "(для выхода нажми ❌ Выйти из режима перевода)",
        reply_markup=translation_mode_keyboard
    )

@dp.message(lambda message: message.text == "😎 Формальный → Неформальный")
async def start_informal_translation(message: types.Message, state: FSMContext):
    await state.set_state(TranslationStates.waiting_for_formal)
    await message.answer(
        "✅ Режим: Формальный → Неформальный\n\n"
        "Отправь формальный текст для перевода:\n"
        "(для выхода нажми ❌ Выйти из режима перевода)",
        reply_markup=translation_mode_keyboard
    )

@dp.message(lambda message: message.text == "❌ Выйти из режима перевода")
async def exit_translation_mode(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "✅ Вышел из режима перевода",
        reply_markup=get_main_keyboard(message.from_user.id)
    )

@dp.message(TranslationStates.waiting_for_informal)
async def handle_informal_text(message: types.Message, state: FSMContext):
    if message.text == "❌ Выйти из режима перевода":
        await state.clear()
        await message.answer("✅ Вышел из режима перевода", reply_markup=get_main_keyboard(message.from_user.id))
        return
    
    if message.content_type != 'text':
        await message.answer("❌ В режиме перевода поддерживаются только текстовые сообщения")
        return
    
    user_text = message.text
    formal_text, explanation = translate_to_formal(user_text, message.from_user.id)
    
    response = f"🎩 Формальный вариант:\n`{formal_text}`"
    if explanation:
        response += f"\n\n📚 Объяснение:\n{explanation}"
    
    await message.answer(response, parse_mode='Markdown', reply_markup=translation_mode_keyboard)

@dp.message(TranslationStates.waiting_for_formal)
async def handle_formal_text(message: types.Message, state: FSMContext):
    if message.text == "❌ Выйти из режима перевода":
        await state.clear()
        await message.answer("✅ Вышел из режима перевода", reply_markup=get_main_keyboard(message.from_user.id))
        return
    
    if message.content_type != 'text':
        await message.answer("❌ В режиме перевода поддерживаются только текстовые сообщения")
        return
    
    user_text = message.text
    informal_text, explanation = translate_to_informal(user_text, message.from_user.id) 
    
    response = f"😎 Неформальный вариант:\n`{informal_text}`"
    if explanation:
        response += f"\n\n📚 Объяснение:\n{explanation}"
    
    await message.answer(response, parse_mode='Markdown', reply_markup=translation_mode_keyboard)
#pragma endregion

#pragma region History & Dictionary Handlers
@dp.message(lambda message: message.text == "📖 История")
async def history_button(message: types.Message):
    await show_history(message)

@dp.message(lambda message: message.text == "📚 Словарь")
async def dictionary_button(message: types.Message):
    await show_dictionary_page(message)

async def show_history(message: types.Message, offset: int = 0):
    translations = db.get_user_translations(message.from_user.id, 1000)
    
    if not translations:
        await message.answer("📭 Ваша история переводов пуста")
        return
    
    if offset >= len(translations):
        offset = 0
    
    page_translations = translations[offset:offset+10]
    
    if not page_translations:
        await message.answer("📭 На этой странице нет переводов")
        return
    
    text = f"📖 Ваша история переводов (стр. {offset//10 + 1} из {(len(translations)-1)//10 + 1}):\n\n"
    for i, trans in enumerate(page_translations, offset + 1):
        direction = trans.get('direction', 'to_formal')
        if direction == 'to_formal':
            text += f"{i}. 🎩 Неформальный → Формальный\n"
            text += f"   😎 `{trans['informal_text']}`\n"
            text += f"   → 🎩 `{trans['formal_text']}`\n"
        else:
            text += f"{i}. 😎 Формальный → Неформальный\n"
            text += f"   🎩 `{trans['informal_text']}`\n"
            text += f"   → 😎 `{trans['formal_text']}`\n"
        text += f"   📅 {trans['created_at']}\n\n"
    
    keyboard_buttons = []
    keyboard_buttons.append([InlineKeyboardButton(text="🔍 Поиск в истории", callback_data="search_history")])
    
    nav_buttons = []
    if offset > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"history_prev_{offset-10}"))
    if offset + 10 < len(translations):
        nav_buttons.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"history_next_{offset+10}"))
    
    if nav_buttons:
        keyboard_buttons.append(nav_buttons)
    
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    if isinstance(message, CallbackQuery):
        await message.message.edit_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await message.answer(text, reply_markup=reply_markup, parse_mode='Markdown')

async def show_dictionary_page(message: types.Message, offset: int = 0):
    words = db.get_dictionary(limit=10, offset=offset)
    total_words = db.get_dictionary_count()
    
    if not words:
        await message.answer("📭 Словарь пуст")
        return
    
    text = f"📚 Словарь слов (стр. {offset//10 + 1}):\n\n"
    for i, word in enumerate(words, offset + 1):
        text += f"{i}. 😎 `{word['informal_text']}` → 🎩 `{word['formal_text']}`"
        if word.get('explanation'):
            text += f"\n   📖 {word['explanation']}\n\n"
        else:
            text += "\n\n"
    
    keyboard_buttons = []
    keyboard_buttons.append([InlineKeyboardButton(text="🔍 Поиск в словаре", callback_data="search_dictionary")])
    
    nav_buttons = []
    if offset > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"dict_prev_{offset-10}"))
    if offset + 10 < total_words:
        nav_buttons.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"dict_next_{offset+10}"))
    
    if nav_buttons:
        keyboard_buttons.append(nav_buttons)
    
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    if isinstance(message, CallbackQuery):
        await message.message.edit_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await message.answer(text, parse_mode='Markdown', reply_markup=reply_markup)
#pragma endregion

#pragma region Search Handlers
@dp.callback_query(lambda c: c.data == "search_history")
async def start_search_history(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SearchStates.waiting_for_search)
    await state.update_data(search_type="history")
    await callback.message.answer(
        "🔍 Введите текст для поиска в истории:\n"
        "(для отмены нажмите ❌ Отменить)",
        reply_markup=cancel_keyboard
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data == "search_dictionary")
async def start_search_dictionary(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SearchStates.waiting_for_search)
    await state.update_data(search_type="dictionary")
    await callback.message.answer(
        "🔍 Введите текст для поиска в словаре:\n"
        "(для отмены нажмите ❌ Отменить)",
        reply_markup=cancel_keyboard
    )
    await callback.answer()

@dp.message(SearchStates.waiting_for_search)
async def handle_search(message: Message, state: FSMContext):
    if message.text == "❌ Отменить":
        await state.clear()
        await message.answer("✅ Поиск отменен", reply_markup=get_main_keyboard(message.from_user.id))
        return
    
    search_text = message.text
    data = await state.get_data()
    search_type = data.get('search_type', 'history')
    
    if search_type == "history":
        results = db.search_user_translations(search_text, message.from_user.id)
    else:
        results = db.search_dictionary(search_text)
    
    if not results:
        await message.answer(f"🔍 По запросу '{search_text}' ничего не найдено")
        await state.clear()
        await message.answer("Возврат в главное меню", reply_markup=get_main_keyboard(message.from_user.id))
        return
    
    await state.update_data(
        search_results=results,
        search_type=search_type,
        search_text=search_text,
        current_offset=0
    )
    
    await show_search_results(message, state, 0)

async def show_search_results(message: Message, state: FSMContext, offset: int = 0):
    data = await state.get_data()
    results = data.get('search_results', [])
    search_type = data.get('search_type', 'history')
    search_text = data.get('search_text', '')
    
    if not results:
        await message.answer("❌ Результаты поиска не найдены")
        return
    
    page_results = results[offset:offset + 10]
    total_pages = (len(results) + 9) // 10
    
    if search_type == "history":
        text = f"🔍 Найдено {len(results)} переводов по запросу '{search_text}'\n"
        text += f"Страница {offset//10 + 1} из {total_pages}:\n\n"
        
        for i, trans in enumerate(page_results, offset + 1):
            direction = trans.get('direction', 'to_formal')
            if direction == 'to_formal':
                text += f"{i}. 🎩 Неформальный → Формальный\n"
                text += f"   😎 `{trans['informal_text']}`\n"
                text += f"   → 🎩 `{trans['formal_text']}`\n"
            else:
                text += f"{i}. 😎 Формальный → Неформальный\n"
                text += f"   🎩 `{trans['informal_text']}`\n"
                text += f"   → 😎 `{trans['formal_text']}`\n"
            text += f"   📅 {trans['created_at']}\n\n"
    
    else:
        text = f"🔍 Найдено {len(results)} слов по запросу '{search_text}'\n"
        text += f"Страница {offset//10 + 1} из {total_pages}:\n\n"
        
        for i, word in enumerate(page_results, offset + 1):
            text += f"{i}. 😎 `{word['informal_text']}` → 🎩 `{word['formal_text']}`"
            if word.get('explanation'):
                text += f"\n   📖 {word['explanation']}\n\n"
            else:
                text += "\n\n"
    
    keyboard_buttons = []
    nav_buttons = []
    
    if offset > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"search_prev_{offset-10}"))
    
    if offset + 10 < len(results):
        nav_buttons.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"search_next_{offset+10}"))
    
    if nav_buttons:
        keyboard_buttons.append(nav_buttons)
    
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    if isinstance(message, CallbackQuery):
        await message.message.edit_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await message.answer(text, reply_markup=reply_markup, parse_mode='Markdown')
    
    await state.update_data(current_offset=offset)

@dp.callback_query(lambda c: c.data.startswith('search_'))
async def handle_search_pagination(callback: CallbackQuery, state: FSMContext):
    try:
        action, offset = callback.data.split('_')[1:]
        offset = int(offset)
        await show_search_results(callback, state, offset)
        await callback.answer()
    except Exception as e:
        await callback.answer("❌ Ошибка при загрузке")
        print(f"❌ Ошибка в handle_search_pagination: {e}")
#pragma endregion

#pragma region Admin Panel Handlers
@dp.message(lambda message: message.text == "⚙️ Админ-панель")
async def admin_panel_button(message: types.Message):
    if not is_user_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав доступа к админ-панели")
        return
    
    admin_role = db.getAdminByLogin(str(message.from_user.id))
    await message.answer(
        f"⚙️ Админ-панель (Ваша роль: {admin_role})\n\n"
        "Выберите действие:",
        reply_markup=get_admin_keyboard(admin_role)
    )

@dp.message(lambda message: message.text == "📝 Управление словарем")
async def dictionary_management_button(message: types.Message):
    if not is_user_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав доступа")
        return
        
    await message.answer(
        "📝 Управление словарем:",
        reply_markup=dictionary_management_keyboard
    )

@dp.message(lambda message: message.text == "⬅️ Назад в админ-панель")
async def back_to_admin_panel(message: types.Message):
    if not is_user_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав доступа")
        return
        
    admin_role = db.getAdminByLogin(str(message.from_user.id))
    await message.answer(
        f"⚙️ Админ-панель (Ваша роль: {admin_role})\n\n"
        "Выберите действие:",
        reply_markup=get_admin_keyboard(admin_role)
    )

@dp.message(lambda message: message.text == "👥 Список админов")
async def show_admins(message: Message):
    if not is_user_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав доступа")
        return
        
    admins = db.getAdmin()
    
    if not admins:
        await message.answer("📭 Список админов пуст")
        return
    
    text = "👥 Список админов:\n\n"
    for admin in admins:
        text += f"🆔 ID: {admin[0]}\n"
        text += f"👤 Логин (User ID): {admin[1]}\n"
        text += f"🎭 Роль: {admin[2]}\n\n"
    
    text += "💡 Для добавления админа используйте ID пользователя Telegram"
    await message.answer(text)

@dp.message(lambda message: message.text == "➕ Добавить админа")
async def add_admin_start(message: Message, state: FSMContext):
    if not is_user_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав доступа")
        return
    
    admin_role = db.getAdminByLogin(str(message.from_user.id))
    if admin_role != "GreatAdmin":
        await message.answer("❌ Только GreatAdmin может добавлять админов", reply_markup=get_admin_keyboard(admin_role))
        return
        
    await state.set_state(AdminStates.waiting_for_admin_login)
    await message.answer(
        "Введите ID пользователя Telegram для добавления в админы:\n"
        "💡 ID можно получить с помощью бота @userinfobot\n"
        "(для отмены нажмите ❌ Отменить)",
        reply_markup=cancel_keyboard
    )

@dp.message(AdminStates.waiting_for_admin_login)
async def add_admin_login(message: Message, state: FSMContext):
    if message.text == "❌ Отменить":
        await state.clear()
        admin_role = db.getAdminByLogin(str(message.from_user.id))
        await message.answer("✅ Добавление админа отменено", reply_markup=get_admin_keyboard(admin_role))
        return
    
    if not message.text.isdigit():
        await message.answer("❌ Введите корректный числовой ID пользователя")
        return
    
    await state.update_data(admin_login=message.text)
    await state.set_state(AdminStates.waiting_for_admin_role)
    
    await message.answer(
        "Выберите роль админа:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="👑 GreatAdmin"), KeyboardButton(text="👤 Admin")],
                [KeyboardButton(text="❌ Отменить")]
            ],
            resize_keyboard=True
        )
    )

@dp.message(AdminStates.waiting_for_admin_role)
async def add_admin_role(message: Message, state: FSMContext):
    if message.text == "❌ Отменить":
        await state.clear()
        admin_role = db.getAdminByLogin(str(message.from_user.id))
        await message.answer("✅ Добавление админа отменено", reply_markup=get_admin_keyboard(admin_role))
        return
    
    role_map = {"👑 GreatAdmin": "GreatAdmin", "👤 Admin": "Admin"}
    if message.text not in role_map:
        await message.answer("❌ Пожалуйста, выберите роль из предложенных вариантов")
        return
    
    data = await state.get_data()
    admin_login = data['admin_login']
    
    db.addAdmin(admin_login, role_map[message.text])
    
    admin_role = db.getAdminByLogin(str(message.from_user.id))
    await message.answer(f"✅ Пользователь с ID {admin_login} добавлен как админ", reply_markup=get_admin_keyboard(admin_role))
    await state.clear()

@dp.message(lambda message: message.text == "➖ Удалить админа")
async def remove_admin_start(message: Message, state: FSMContext):
    if not is_user_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав доступа")
        return
    
    admin_role = db.getAdminByLogin(str(message.from_user.id))
    if admin_role != "GreatAdmin":
        await message.answer("❌ Только GreatAdmin может удалять админов", reply_markup=get_admin_keyboard(admin_role))
        return
        
    await state.set_state(AdminStates.waiting_for_admin_remove)
    await message.answer(
        "Введите ID админа для удаления:\n"
        "(для отмены нажмите ❌ Отменить)",
        reply_markup=cancel_keyboard
    )

@dp.message(AdminStates.waiting_for_admin_remove)
async def remove_admin_execute(message: Message, state: FSMContext):
    if message.text == "❌ Отменить":
        await state.clear()
        admin_role = db.getAdminByLogin(str(message.from_user.id))
        await message.answer("✅ Удаление админа отменено", reply_markup=get_admin_keyboard(admin_role))
        return
    
    try:
        admin_id = int(message.text)
        db.removeAdminByID(admin_id)
        admin_role = db.getAdminByLogin(str(message.from_user.id))
        await message.answer(f"✅ Админ с ID {admin_id} удален", reply_markup=get_admin_keyboard(admin_role))
    except ValueError:
        await message.answer("❌ Введите корректный ID (число)")
        return
    
    await state.clear()

@dp.message(lambda message: message.text == "📊 Статистика")
async def show_admin_stats(message: Message):
    if not is_user_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав доступа")
        return
        
    stats = db.get_stats()
    
    text = (
        "📊 Статистика системы:\n\n"
        f"• 📖 Всего переводов: {stats.get('total_translations', 0)}\n"
        f"• 📚 Слов в словаре: {stats.get('total_words', 0)}\n"
        f"• 🔢 Всего использований: {stats.get('total_usage', 0)}"
    )
    
    await message.answer(text)
#pragma endregion

#pragma region Dictionary Management Handlers
@dp.message(lambda message: message.text == "➕ Добавить слово")
async def add_word_start(message: Message, state: FSMContext):
    if not is_user_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав доступа")
        return
        
    await state.set_state(AddWordStates.waiting_for_informal)
    await message.answer(
        "Введите неформальное слово/фразу:\n"
        "(для отмены нажмите ❌ Отменить)",
        reply_markup=cancel_keyboard
    )

@dp.message(AddWordStates.waiting_for_informal)
async def add_word_informal(message: Message, state: FSMContext):
    if message.text == "❌ Отменить":
        await state.clear()
        await message.answer("✅ Добавление слова отменено", reply_markup=dictionary_management_keyboard)
        return
    
    await state.update_data(informal=message.text)
    await state.set_state(AddWordStates.waiting_for_formal)
    
    await message.answer(
        "Введите формальный вариант:\n"
        "(для отмены нажмите ❌ Отменить)",
        reply_markup=cancel_keyboard
    )

@dp.message(AddWordStates.waiting_for_formal)
async def add_word_formal(message: Message, state: FSMContext):
    if message.text == "❌ Отменить":
        await state.clear()
        await message.answer("✅ Добавление слова отменено", reply_markup=dictionary_management_keyboard)
        return
    
    await state.update_data(formal=message.text)
    await state.set_state(AddWordStates.waiting_for_explanation)
    
    await message.answer(
        "Введите объяснение (или отправьте '-' чтобы пропустить):\n"
        "(для отмены нажмите ❌ Отменить)",
        reply_markup=cancel_keyboard
    )

@dp.message(AddWordStates.waiting_for_explanation)
async def add_word_explanation(message: Message, state: FSMContext):
    if message.text == "❌ Отменить":
        await state.clear()
        await message.answer("✅ Добавление слова отменено", reply_markup=dictionary_management_keyboard)
        return
    
    data = await state.get_data()
    informal = data['informal']
    formal = data['formal']
    explanation = message.text if message.text != '-' else ''
    
    if db.add_to_dictionary(informal, formal, explanation):
        response = f"✅ Слово добавлено в словарь:\n😎 `{informal}` → 🎩 `{formal}`"
        if explanation:
            response += f"\n📚 {explanation}"
        await message.answer(response, parse_mode='Markdown', reply_markup=dictionary_management_keyboard)
    else:
        await message.answer("❌ Ошибка добавления слова", reply_markup=dictionary_management_keyboard)
    
    await state.clear()

@dp.message(lambda message: message.text == "➖ Удалить слово")
async def delete_word_start(message: Message, state: FSMContext):
    if not is_user_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав доступа")
        return
        
    await state.set_state(DeleteWordStates.waiting_for_word_input)
    await message.answer(
        "Введите неформальное слово для удаления:\n"
        "💡 Вы можете посмотреть слова в словаре\n"
        "(для отмены нажмите ❌ Отменить)",
        reply_markup=cancel_keyboard
    )

@dp.message(DeleteWordStates.waiting_for_word_input)
async def delete_word_input(message: Message, state: FSMContext):
    if message.text == "❌ Отменить":
        await state.clear()
        await message.answer("✅ Удаление слова отменено", reply_markup=dictionary_management_keyboard)
        return
    
    word_text = message.text.strip()
    word = db.get_word_by_informal(word_text)
    
    if not word:
        await message.answer(f"❌ Слово `{word_text}` не найдено в словаре")
        return
    
    await state.update_data(word_to_delete=word_text)
    await state.set_state(DeleteWordStates.waiting_for_confirmation)
    
    text = f"⚠️ Вы уверены, что хотите удалить слово?\n\n"
    text += f"😎 `{word['informal_text']}` → 🎩 `{word['formal_text']}`"
    if word.get('explanation'):
        text += f"\n📚 {word['explanation']}"
    
    await message.answer(text, parse_mode='Markdown', reply_markup=confirm_keyboard)

@dp.message(DeleteWordStates.waiting_for_confirmation)
async def delete_word_confirmation(message: Message, state: FSMContext):
    if message.text == "❌ Отменить":
        await state.clear()
        await message.answer("✅ Удаление слова отменено", reply_markup=dictionary_management_keyboard)
        return
    
    if message.text == "✅ Да, удалить":
        data = await state.get_data()
        word_text = data['word_to_delete']
        
        if db.delete_from_dictionary(word_text):
            await message.answer(f"✅ Слово `{word_text}` удалено из словаря", reply_markup=dictionary_management_keyboard)
        else:
            await message.answer(f"❌ Ошибка при удалении слова `{word_text}`", reply_markup=dictionary_management_keyboard)
    else:
        await message.answer("❌ Пожалуйста, выберите действие из предложенных кнопок")
        return
    
    await state.clear()
#pragma endregion

#pragma region Pagination Handlers
@dp.callback_query(lambda c: c.data.startswith('history_'))
async def handle_history_pagination(callback: CallbackQuery):
    try:
        action, offset = callback.data.split('_')[1:]
        offset = int(offset)
        await show_history(callback, offset)
        await callback.answer()
    except Exception as e:
        await callback.answer("❌ Ошибка при загрузке")
        print(f"❌ Ошибка в handle_history_pagination: {e}")

@dp.callback_query(lambda c: c.data.startswith('dict_'))
async def handle_dictionary_pagination(callback: CallbackQuery):
    try:
        action, offset = callback.data.split('_')[1:]
        offset = int(offset)
        await show_dictionary_page(callback, offset)
        await callback.answer()
    except Exception as e:
        await callback.answer("❌ Ошибка при загрузке")
        print(f"❌ Ошибка в handle_dictionary_pagination: {e}")
#pragma endregion

#pragma region Any Message Handler
@dp.message()
async def handle_any_message(message: Message, state: FSMContext):
    if message.content_type not in ['text']:
        current_state = await state.get_state()
        if current_state:
            if current_state in [TranslationStates.waiting_for_informal.state, 
                               TranslationStates.waiting_for_formal.state]:
                await message.answer("❌ В режиме перевода поддерживаются только текстовые сообщения")
                return
        
        await message.answer(
            "❌ Поддерживаются только текстовые сообщения\n\n"
            "📝 Пожалуйста, используйте кнопки меню для выбора действия:\n"
            "• 🔄 Перевод - для перевода текста\n"
            "• 📖 История - для просмотра истории переводов\n"
            "• 📚 Словарь - для просмотра словаря\n"
            "• ⚙️ Админ-панель - для управления (если вы админ)",
            reply_markup=get_main_keyboard(message.from_user.id)
        )
        return
    
    system_buttons = [
        "🔄 Перевод", "📖 История", "📚 Словарь", "⚙️ Админ-панель",
        "🎩 Неформальный → Формальный", "😎 Формальный → Неформальный",
        "❌ Выйти из режима перевода", "⬅️ Назад в меню",
        "👥 Список админов", "➕ Добавить админа", "➖ Удалить админа",
        "📊 Статистика", "📝 Управление словарем", "⬅️ Назад в админ-панель",
        "➕ Добавить слово", "➖ Удалить слово", "❌ Отменить",
        "✅ Да, удалить", "❌ Нет, отменить", "👑 GreatAdmin", "👤 Admin"
    ]
    
    if message.text in system_buttons or message.text.startswith('/'):
        return
    
    current_state = await state.get_state()
    
    if current_state:
        if len(message.text.strip()) < 1:
            await message.answer("❌ Введите текст для перевода")
            return
        
        try:
            if current_state == TranslationStates.waiting_for_informal.state:
                user_text = message.text
                formal_text, explanation = translate_to_formal(user_text, message.from_user.id)
                
                response = f"🎩 Формальный вариант:\n`{formal_text}`"
                if explanation:
                    response += f"\n\n📚 Объяснение:\n{explanation}"
                
                await message.answer(response, parse_mode='Markdown', reply_markup=translation_mode_keyboard)
                
            elif current_state == TranslationStates.waiting_for_formal.state:
                user_text = message.text
                informal_text, explanation = translate_to_informal(user_text, message.from_user.id)
                
                response = f"😎 Неформальный вариант:\n`{informal_text}`"
                if explanation:
                    response += f"\n\n📚 Объяснение:\n{explanation}"
                
                await message.answer(response, parse_mode='Markdown', reply_markup=translation_mode_keyboard)
                
            else:
                return
                
        except Exception as e:
            await message.answer("❌ Произошла ошибка при обработке сообщения")
            print(f"❌ Ошибка в handle_any_message: {e}")
    
    else:
        await message.answer(
            "❌ Вы не выбрали режим работы.\n\n"
            "📝 Пожалуйста, используйте кнопки меню для выбора действия:\n"
            "• 🔄 Перевод - для перевода текста\n"
            "• 📖 История - для просмотра истории переводов\n"
            "• 📚 Словарь - для просмотра словаря\n"
            "• ⚙️ Админ-панель - для управления (если вы админ)",
            reply_markup=get_main_keyboard(message.from_user.id)
        )
#pragma endregion

#pragma region Main
async def main():
    print("✅ Бот запущен!")
    print("✅ База данных: translations.db")
    print("📝 Просто пишите сообщения - они автоматически сохранятся!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
#pragma endregion