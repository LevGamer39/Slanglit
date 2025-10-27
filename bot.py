# bot.py
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
import sqlite3
from database import FDataBase
from typing import Tuple, Optional
from secret import BOT_TOKEN
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


def connect_db():
    return sqlite3.connect('translations.db')
db = FDataBase(connect_db())
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def translate_to_formal(text: str, user_id: int = None) -> Tuple[str, Optional[str]]:
    original_text = text
    result = db.get_formal_translation(text.lower())
    if result:
        formal_text, explanation = result
        explanation_text = f"{text} → {formal_text}: {explanation}" if explanation else None
        db.add_translation(text, formal_text, explanation_text, user_id)
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
    
    db.add_translation(text, formal_text, explanation_text, user_id)
    
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
    
    db.add_translation(text, informal_text, explanation_text, user_id)
    
    return informal_text, explanation_text


class TranslationStates(StatesGroup):
    waiting_for_informal = State()
    waiting_for_formal = State()

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📖 История"), KeyboardButton(text="📚 Словарь")],
        [KeyboardButton(text="🔍 Поиск"), KeyboardButton(text="🔄 Перевод")]
    ],
    resize_keyboard=True
)

translation_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎩 Неформальный → Формальный")],
        [KeyboardButton(text="😎 Формальный → Неформальный")],
        [KeyboardButton(text="⬅️ Назад")]
    ],
    resize_keyboard=True
)

translation_mode_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="❌ Выйти из режима перевода")]],
    resize_keyboard=True
)


@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer(
        "👋 Привет! Я бот для перевода между формальным и неформальным стилем.\n\n"
        "📝 Используй кнопки для навигации!",
        reply_markup=main_keyboard
    )


@dp.message(TranslationStates.waiting_for_informal)
async def handle_informal_text(message: types.Message, state: FSMContext):
    if message.text == "❌ Выйти из режима перевода":
        await state.clear()
        await message.answer("✅ Вышел из режима перевода", reply_markup=main_keyboard)
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
        await message.answer("✅ Вышел из режима перевода", reply_markup=main_keyboard)
        return
    
    user_text = message.text
    informal_text, explanation = translate_to_informal(user_text, message.from_user.id) 
    
    response = f"😎 Неформальный вариант:\n`{informal_text}`"
    if explanation:
        response += f"\n\n📚 Объяснение:\n{explanation}"
    
    await message.answer(response, parse_mode='Markdown', reply_markup=translation_mode_keyboard)


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
    current_state = await state.get_state()
    if current_state is not None:
        await state.clear()
    await message.answer(
        "✅ Вышел из режима перевода",
        reply_markup=main_keyboard
    )

@dp.message(lambda message: message.text == "🔄 Перевод")
async def show_translation_options(message: types.Message):
    await message.answer(
        "🔄 Выбери направление перевода:",
        reply_markup=translation_keyboard
    )

@dp.message(lambda message: message.text == "📖 История")
async def history_button(message: types.Message):
    await show_history(message)

@dp.message(lambda message: message.text == "📚 Словарь")
async def dictionary_button(message: types.Message):
    await show_dictionary(message)

@dp.message(lambda message: message.text == "🔍 Поиск")
async def search_button(message: types.Message):
    await message.answer("🔍 Введите команду: /search <текст>")

@dp.message(lambda message: message.text == "⬅️ Назад")
async def go_back_to_mode_selection(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is not None:
        await state.clear()
    await message.answer(
        "🔄 Выбери направление перевода:",
        reply_markup=translation_keyboard
    )



@dp.message(Command("help"))
async def help_command(message: types.Message):
    await message.answer(
        "ℹ️ Как пользоваться ботом:\n\n"
        "1. 📝 Напиши любое сообщение (например: 'привет бро')\n"
        "2. 🤖 Бот ответит формальным вариантом\n"
        "3. 💾 Перевод автоматически сохранится в базу\n"
        "4. 📖 Смотри историю командой /history\n"
        "5. 📚 Смотри словарь командой /dictionary\n"
        "6. 🔍 Ищи переводы командой /search\n\n"
        "Пример: /search кринж"
    )


@dp.message(Command("history"))
async def show_history(message: types.Message):
    translations = db.get_user_translations(message.from_user.id)
    
    if not translations:
        await message.answer("📭 Ваша история переводов пуста")
        return
    
    page_translations = translations[:5]
    
    text = "📖 Ваша история переводов:\n\n"
    for i, trans in enumerate(page_translations, 1):
        text += f"{i}. 😎 `{trans['informal_text']}`\n"
        text += f"   🎩 `{trans['formal_text']}`\n"
        text += f"   📅 {trans['created_at']}\n\n"
    
    keyboard = []
    if len(translations) > 5:
        keyboard.append([InlineKeyboardButton(text="➡️ Показать еще", callback_data=f"next_5_{message.from_user.id}")])  # Добавлен user_id в callback
    keyboard.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="history_back")])
    
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await message.answer(text, reply_markup=reply_markup, parse_mode='Markdown')



@dp.message(Command("dictionary"))
async def show_dictionary(message: types.Message):
    words = db.get_dictionary()
    
    if not words:
        await message.answer("📭 Словарь пуст")
        return
    
    text = "📚 Словарь слов:\n\n"
    for i, word in enumerate(words, 1):
        text += f"{i}. 😎 `{word['informal_text']}` → 🎩 `{word['formal_text']}`"
        if word.get('explanation'):
            text += f"\n   📖 {word['explanation']}\n\n"
        else:
            text += "\n\n"
    
    await message.answer(text, parse_mode='Markdown')


@dp.message(Command("search"))
async def search_translations(message: types.Message):
    try:
        parts = message.text.split(' ', 1)
        if len(parts) < 2:
            await message.answer("❌ Используйте: /search <текст>\nНапример: /search кринж")
            return
            
        search_text = parts[1].strip()
        
        if not search_text:
            await message.answer("❌ Введите текст для поиска")
            return
            
        results = db.search_user_translations(search_text, message.from_user.id)
        
        if not results:
            await message.answer(f"🔍 По запросу '{search_text}' ничего не найдено в вашей истории")
            return
        
        text = f"🔍 Найдено {len(results)} переводов в вашей истории:\n\n"
        for i, trans in enumerate(results, 1):
            text += f"{i}. 😎 `{trans['informal_text']}`\n"
            text += f"   🎩 `{trans['formal_text']}`\n"
            text += f"   📅 {trans['created_at']}\n\n"
        
        await message.answer(text, parse_mode='Markdown')
        
    except Exception as e:
        await message.answer("❌ Ошибка при поиске")
        print(f"❌ Ошибка в /search: {e}")


@dp.message(Command("stats"))
async def show_stats(message: types.Message):
    user_stats = db.get_user_stats(message.from_user.id)
    global_stats = db.get_stats()
    
    text = (
        "📊 Ваша статистика:\n\n"
        f"• 📖 Ваших переводов: {user_stats.get('user_translations', 0)}\n"
        f"• 🔢 Ваших использований: {user_stats.get('user_usage', 0)}\n\n"
        "📊 Общая статистика базы:\n"
        f"• 📚 Слов в словаре: {global_stats.get('total_words', 0)}"
    )
    
    await message.answer(text)


@dp.message(Command("add_word"))
async def add_word_command(message: types.Message):
    try:
        text = message.text.strip()
        parts = text.split(' ', 1)
        
        if len(parts) < 2:
            await message.answer(
                '❌ Используйте: /add_word неформальный формальный [объяснение]\n\n'
                'Примеры:\n'
                '/add_word кринж неловко\n'
                '/add_word "го в доту" "пошли в Dota 2" "Призыв поиграть в игру Dota 2"\n'
                '/add_word бро уважаемый коллега неформальное обращение к другу'
            )
            return
        args_text = parts[1]
        
        import shlex
        try:
            args = shlex.split(args_text)
        except:
            args = args_text.split(' ', 2)
        
        if len(args) < 2:
            await message.answer(
                '❌ Недостаточно аргументов. Используйте:\n'
                '/add_word "неформальный" "формальный" "объяснение"\n\n'
                'Пример:\n'
                '/add_word "го в доту" "пошли в Dota 2" "Призыв поиграть в игру Dota 2"'
            )
            return
            
        informal = args[0]
        formal = args[1]
        explanation = args[2] if len(args) > 2 else ''
        
        if db.add_to_dictionary(informal, formal, explanation):
            response = f"✅ Добавлено в словарь:\n😎 `{informal}` → 🎩 `{formal}`"
            if explanation:
                response += f"\n📚 {explanation}"
            await message.answer(response, parse_mode='Markdown')
        else:
            await message.answer("❌ Ошибка добавления в словарь")
            
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")



@dp.callback_query(lambda c: c.data.startswith('next_'))
async def show_more(callback: CallbackQuery):
    try:
        parts = callback.data.split('_')
        offset = int(parts[1])
        user_id = int(parts[2]) if len(parts) > 2 else callback.from_user.id
        
        translations = db.get_user_translations(user_id, limit=1000)
        
        page_translations = translations[offset:offset+5]
        
        if not page_translations:
            await callback.answer("Больше переводов нет")
            return
        
        text = "📖 Ваша история переводов:\n\n"
        for i, trans in enumerate(page_translations, offset + 1):
            text += f"{i}. 😎 `{trans['informal_text']}`\n"
            text += f"   🎩 `{trans['formal_text']}`\n"
            text += f"   📅 {trans['created_at']}\n\n"
        
        keyboard_buttons = []
        if offset > 0:
            keyboard_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"next_{offset-5}_{user_id}"))
        if offset + 5 < len(translations):
            keyboard_buttons.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"next_{offset+5}_{user_id}"))
        
        reply_markup = InlineKeyboardMarkup(inline_keyboard=[keyboard_buttons])
        
        await callback.message.edit_text(text, reply_markup=reply_markup, parse_mode='Markdown')
        await callback.answer()
    except Exception as e:
        await callback.answer("❌ Ошибка при загрузке")
        print(f"❌ Ошибка в show_more: {e}")


@dp.message()
async def handle_any_message(message: Message):
    if not message.text or message.text.startswith('/'):
        return
    
    try:
        user_text = message.text
        formal_text, explanation = translate_to_formal(user_text, message.from_user.id)
        
        response = f"🎩 Формальный вариант:\n`{formal_text}`"
        
        if explanation:
            response += f"\n\n📚 Объяснение:\n{explanation}"
        
        response += f"\n\n💾 Сохранено в базу!"
        
        await message.answer(response, parse_mode='Markdown')
    except Exception as e:
        await message.answer("❌ Произошла ошибка при обработке сообщения")
        print(f"❌ Ошибка в handle_any_message: {e}")


async def main():
    print("✅ Бот запущен!")
    print("✅ База данных: translations.db")
    print("📝 Просто пишите сообщения - они автоматически сохранятся!")
    print("👀 Используйте /history для просмотра истории")
    print("📚 Используйте /dictionary для просмотра словаря")
    print("🔍 Используйте /search для поиска переводов")
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())