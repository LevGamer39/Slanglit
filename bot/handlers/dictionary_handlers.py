from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from utils.keyboards import (get_main_keyboard, cancel_keyboard, dictionary_management_keyboard, 
                           confirm_keyboard, get_dictionary_main_keyboard, get_alphabet_keyboard,
                           get_letter_navigation_keyboard)
from utils.states import AddWordStates, DeleteWordStates, SearchStates
from services.dictionary_service import DictionaryService

router = Router()

# Главное меню словаря
@router.message(lambda message: message.text == "📚 Словарь")
async def dictionary_main_menu(message: types.Message):
    await message.answer(
        "📚 Словарь\n\n"
        "Выберите способ просмотра:",
        reply_markup=get_dictionary_main_keyboard()
    )

@router.message(lambda message: message.text == "⬅️ Назад в словарь")
async def back_to_dictionary_main(message: types.Message):
    await dictionary_main_menu(message)

# Обработка кнопки поиска в словаре
@router.message(lambda message: message.text == "🔍 Поиск в словаре")
async def search_dictionary_button(message: types.Message, state: FSMContext):
    await state.set_state(SearchStates.waiting_for_search)
    await state.update_data(search_type="dictionary")
    await message.answer(
        "🔍 Введите текст для поиска в словаре:\n"
        "(для отмены нажмите ❌ Отменить)",
        reply_markup=cancel_keyboard
    )

# Алфавитный просмотр
@router.message(lambda message: message.text == "🔤 По алфавиту")
async def show_alphabet(message: types.Message, dictionary_service: DictionaryService):
    alphabet_stats = dictionary_service.get_alphabet_stats()
    
    text = "🔤 Выберите букву для просмотра слов:\n\n"
    
    # Показываем статистику по буквам
    russian_alphabet = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
    stats_lines = []
    
    for i in range(0, len(russian_alphabet), 9):
        line_letters = russian_alphabet[i:i+9]
        stats_line = ""
        for letter in line_letters:
            count = alphabet_stats.get(letter, 0)
            stats_line += f"{letter}:{count} "
        stats_lines.append(stats_line)
    
    text += "📊 Статистика по буквам:\n"
    text += "\n".join(stats_lines)
    
    text += "\n\nALL - все слова"
    
    await message.answer(text, reply_markup=get_alphabet_keyboard())

# Просмотр всех слов (старый способ)
@router.message(lambda message: message.text == "📄 Все слова")
async def show_all_words(message: types.Message, dictionary_service: DictionaryService):
    await show_dictionary_page(message, dictionary_service)

async def show_dictionary_page(message: types.Message, dictionary_service: DictionaryService, offset: int = 0):
    words = dictionary_service.get_dictionary_page(limit=10, offset=offset)
    total_words = dictionary_service.get_dictionary_count()
    
    if not words:
        await message.answer("📭 Словарь пуст")
        return
    
    text = f"📚 Все слова (стр. {offset//10 + 1} из {(total_words-1)//10 + 1}):\n\n"
    for i, word in enumerate(words, offset + 1):
        text += f"{i}.\t🔥 `{word['informal_text']}`\n"
        text += f"\t💼 `{word['formal_text']}`"
        if word.get('explanation'):
            text += f"\n\t📖 {word['explanation']}\n\n"
        else:
            text += "\n\n"
    
    keyboard_buttons = []
    keyboard_buttons.append([InlineKeyboardButton(text="🔍 Поиск в словаре", callback_data="search_dictionary")])
    keyboard_buttons.append([InlineKeyboardButton(text="🔤 Перейти к алфавиту", callback_data="show_alphabet")])
    
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

# Обработка выбора буквы - ИСПРАВЛЕННЫЙ ХЕНДЛЕР
@router.message(lambda message: message.text and (
    message.text in [chr(i) for i in range(1040, 1072)] + ['Ё', 'ALL', '0-9'] or 
    (message.text.startswith('🔘 ') and message.text.replace('🔘 ', '').strip() in [chr(i) for i in range(1040, 1072)] + ['Ё', 'ALL', '0-9'])
))
async def show_words_by_letter(message: types.Message, dictionary_service: DictionaryService):
    # Извлекаем букву из текста (убираем эмодзи если есть)
    letter_text = message.text.replace('🔘 ', '').strip()
    
    if letter_text == 'ALL':
        await show_all_words(message, dictionary_service)
        return
    
    await show_letter_words(message, dictionary_service, letter_text, 0)

async def show_letter_words(message: types.Message, dictionary_service: DictionaryService, letter: str, offset: int = 0):
    if letter == '0-9':
        # Для цифр и символов используем специальную логику
        words = dictionary_service.get_words_by_letter('0-9', 1000)  # Большой лимит для цифр
        total_words = dictionary_service.get_words_count_by_letter('0-9')
        page_words = words[offset:offset+10]
    else:
        words = dictionary_service.get_words_by_letter(letter, 10, offset)
        total_words = dictionary_service.get_words_count_by_letter(letter)
        page_words = words
    
    if not page_words:
        await message.answer(f"📭 На букву '{letter}' слов не найдено")
        return
    
    if letter == '0-9':
        text = f"🔢 Цифры и символы (стр. {offset//10 + 1} из {(total_words-1)//10 + 1}):\n\n"
    else:
        text = f"🔤 Слова на букву '{letter}' (стр. {offset//10 + 1} из {(total_words-1)//10 + 1}):\n\n"
    
    for i, word in enumerate(page_words, offset + 1):
        text += f"{i}.\t🔥 `{word['informal_text']}`\n"
        text += f"\t💼 `{word['formal_text']}`"
        if word.get('explanation'):
            text += f"\n\t📖 {word['explanation']}\n\n"
        else:
            text += "\n\n"
    
    reply_markup = get_letter_navigation_keyboard(letter, offset, total_words)
    
    if isinstance(message, CallbackQuery):
        await message.message.edit_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await message.answer(text, parse_mode='Markdown', reply_markup=reply_markup)

# Обработка навигации по буквам
@router.callback_query(lambda c: c.data.startswith('letter_'))
async def handle_letter_pagination(callback: CallbackQuery, dictionary_service: DictionaryService):
    try:
        # Формат: letter_{letter}_{action}_{offset}
        parts = callback.data.split('_')
        letter = parts[1]
        action = parts[2]
        offset = int(parts[3])
        
        await show_letter_words(callback, dictionary_service, letter, offset)
        await callback.answer()
    except Exception as e:
        await callback.answer("❌ Ошибка при загрузке")
        print(f"❌ Ошибка в handle_letter_pagination: {e}")

@router.callback_query(lambda c: c.data == "back_to_alphabet")
async def back_to_alphabet(callback: CallbackQuery, dictionary_service: DictionaryService):
    await callback.message.delete()
    await show_alphabet(callback.message, dictionary_service)

@router.callback_query(lambda c: c.data == "show_alphabet")
async def show_alphabet_callback(callback: CallbackQuery, dictionary_service: DictionaryService):
    await callback.message.delete()
    await show_alphabet(callback.message, dictionary_service)

# Старая пагинация для совместимости
@router.callback_query(lambda c: c.data.startswith('dict_'))
async def handle_dictionary_pagination(callback: CallbackQuery, dictionary_service: DictionaryService):
    try:
        action, offset = callback.data.split('_')[1:]
        offset = int(offset)
        await show_dictionary_page(callback, dictionary_service, offset)
        await callback.answer()
    except Exception as e:
        await callback.answer("❌ Ошибка при загрузке")
        print(f"❌ Ошибка в handle_dictionary_pagination: {e}")

# Поиск в словаре (из инлайн кнопки)
@router.callback_query(lambda c: c.data == "search_dictionary")
async def start_search_dictionary_callback(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SearchStates.waiting_for_search)
    await state.update_data(search_type="dictionary")
    await callback.message.answer(
        "🔍 Введите текст для поиска в словаре:\n"
        "(для отмены нажмите ❌ Отменить)",
        reply_markup=cancel_keyboard
    )
    await callback.answer()

# Админские функции (добавление/удаление слов)
@router.message(lambda message: message.text == "➕ Добавить слово")
async def add_word_start(message: types.Message, state: FSMContext):
    await state.set_state(AddWordStates.waiting_for_informal)
    await message.answer(
        "Введите неформальное слово/фразу:\n"
        "(для отмены нажмите ❌ Отменить)",
        reply_markup=cancel_keyboard
    )

@router.message(AddWordStates.waiting_for_informal)
async def add_word_informal(message: types.Message, state: FSMContext):
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

@router.message(AddWordStates.waiting_for_formal)
async def add_word_formal(message: types.Message, state: FSMContext):
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

@router.message(AddWordStates.waiting_for_explanation)
async def add_word_explanation(message: types.Message, state: FSMContext, dictionary_service: DictionaryService):
    if message.text == "❌ Отменить":
        await state.clear()
        await message.answer("✅ Добавление слова отменено", reply_markup=dictionary_management_keyboard)
        return
    
    data = await state.get_data()
    informal = data['informal']
    formal = data['formal']
    explanation = message.text if message.text != '-' else ''
    
    if dictionary_service.add_word(informal, formal, explanation):
        response = f"✅ Слово добавлено в словарь:\n🔥 `{informal}` → 💼 `{formal}`"
        if explanation:
            response += f"\n📚 {explanation}"
        await message.answer(response, parse_mode='Markdown', reply_markup=dictionary_management_keyboard)
    else:
        await message.answer("❌ Ошибка добавления слова", reply_markup=dictionary_management_keyboard)
    
    await state.clear()

@router.message(lambda message: message.text == "➖ Удалить слово")
async def delete_word_start(message: types.Message, state: FSMContext):
    await state.set_state(DeleteWordStates.waiting_for_word_input)
    await message.answer(
        "Введите неформальное слово для удаления:\n"
        "💡 Вы можете посмотреть слова в словаре\n"
        "(для отмены нажмите ❌ Отменить)",
        reply_markup=cancel_keyboard
    )

@router.message(DeleteWordStates.waiting_for_word_input)
async def delete_word_input(message: types.Message, state: FSMContext, dictionary_service: DictionaryService):
    if message.text == "❌ Отменить":
        await state.clear()
        await message.answer("✅ Удаление слова отменено", reply_markup=dictionary_management_keyboard)
        return
    
    word_text = message.text.strip()
    word = dictionary_service.get_word_by_informal(word_text)
    
    if not word:
        await message.answer(f"❌ Слово `{word_text}` не найдено в словаре")
        return
    
    await state.update_data(word_to_delete=word_text)
    await state.set_state(DeleteWordStates.waiting_for_confirmation)
    
    text = f"⚠️ Вы уверены, что хотите удалить слово?\n\n"
    text += f"🔥 `{word['informal_text']}` → 💼 `{word['formal_text']}`"
    if word.get('explanation'):
        text += f"\n📚 {word['explanation']}"
    
    await message.answer(text, parse_mode='Markdown', reply_markup=confirm_keyboard)

@router.message(DeleteWordStates.waiting_for_confirmation)
async def delete_word_confirmation(message: types.Message, state: FSMContext, dictionary_service: DictionaryService):
    if message.text == "❌ Отменить":
        await state.clear()
        await message.answer("✅ Удаление слова отменено", reply_markup=dictionary_management_keyboard)
        return
    
    if message.text == "✅ Да, удалить":
        data = await state.get_data()
        word_text = data['word_to_delete']
        
        if dictionary_service.delete_word(word_text):
            await message.answer(f"✅ Слово `{word_text}` удалено из словаря", reply_markup=dictionary_management_keyboard)
        else:
            await message.answer(f"❌ Ошибка при удалении слова `{word_text}`", reply_markup=dictionary_management_keyboard)
    else:
        await message.answer("❌ Пожалуйста, выберите действие из предложенных кнопок")
        return
    
    await state.clear()