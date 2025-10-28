from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from utils.keyboards import get_main_keyboard, cancel_keyboard, dictionary_management_keyboard, confirm_keyboard
from utils.states import AddWordStates, DeleteWordStates
from services.dictionary_service import DictionaryService

router = Router()

@router.message(lambda message: message.text == "📚 Словарь")
async def dictionary_button(message: types.Message, dictionary_service: DictionaryService):
    await show_dictionary_page(message, dictionary_service)

async def show_dictionary_page(message: types.Message, dictionary_service: DictionaryService, offset: int = 0):
    words = dictionary_service.get_dictionary_page(limit=10, offset=offset)
    total_words = dictionary_service.get_dictionary_count()
    
    if not words:
        await message.answer("📭 Словарь пуст")
        return
    
    text = f"📚 Словарь слов (стр. {offset//10 + 1} из {(total_words-1)//10 + 1}):\n\n"
    for i, word in enumerate(words, offset + 1):
        text += f"{i}. 🔥 `{word['informal_text']}` → 💼 `{word['formal_text']}`"
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