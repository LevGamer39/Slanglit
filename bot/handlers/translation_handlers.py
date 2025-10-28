from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from utils.keyboards import translation_keyboard, translation_mode_keyboard, get_main_keyboard
from utils.states import TranslationStates
from services.translation_service import TranslationService

router = Router()

@router.message(lambda message: message.text == "🔄 Перевод")
async def show_translation_options(message: types.Message):
    await message.answer(
        "🔄 Выбери направление перевода:\n\n"
        "🤖 Переводчик: GigaChat Neural Network",
        reply_markup=translation_keyboard
    )

@router.message(lambda message: message.text == "💼 Неформальный → Формальный")
async def start_formal_translation(message: types.Message, state: FSMContext):
    await state.set_state(TranslationStates.waiting_for_informal)
    await message.answer(
        "✅ Режим: Неформальный → Формальный\n"
        "🤖 Переводчик: GigaChat\n\n"
        "Отправь неформальный текст для перевода:\n"
        "(для выхода нажми ❌ Выйти из режима перевода)",
        reply_markup=translation_mode_keyboard
    )

@router.message(lambda message: message.text == "🔥 Формальный → Неформальный")
async def start_informal_translation(message: types.Message, state: FSMContext):
    await state.set_state(TranslationStates.waiting_for_formal)
    await message.answer(
        "✅ Режим: Формальный → Неформальный\n"
        "🤖 Переводчик: GigaChat\n\n"
        "Отправь формальный текст для перевода:\n"
        "(для выхода нажми ❌ Выйти из режима перевода)",
        reply_markup=translation_mode_keyboard
    )

@router.message(lambda message: message.text == "❌ Выйти из режима перевода")
async def exit_translation_mode(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "✅ Вышел из режима перевода",
        reply_markup=get_main_keyboard(message.from_user.id)
    )

@router.message(TranslationStates.waiting_for_informal)
async def handle_informal_text(message: types.Message, state: FSMContext, translation_service: TranslationService):
    if message.text == "❌ Выйти из режима перевода":
        await state.clear()
        await message.answer("✅ Вышел из режима перевода", reply_markup=get_main_keyboard(message.from_user.id))
        return
    
    if message.content_type != 'text':
        await message.answer("❌ В режиме перевода поддерживаются только текстовые сообщения")
        return
    
    user_text = message.text
    formal_text, explanation = translation_service.translate_to_formal(user_text, message.from_user.id)
    
    response = f"💼 Формальный вариант:\n`{formal_text}`"
    if explanation:
        response += f"\n\n📚 Объяснение:\n{explanation}"
    
    await message.answer(response, parse_mode='Markdown', reply_markup=translation_mode_keyboard)

@router.message(TranslationStates.waiting_for_formal)
async def handle_formal_text(message: types.Message, state: FSMContext, translation_service: TranslationService):
    if message.text == "❌ Выйти из режима перевода":
        await state.clear()
        await message.answer("✅ Вышел из режима перевода", reply_markup=get_main_keyboard(message.from_user.id))
        return
    
    if message.content_type != 'text':
        await message.answer("❌ В режиме перевода поддерживаются только текстовые сообщения")
        return
    
    user_text = message.text
    informal_text, explanation = translation_service.translate_to_informal(user_text, message.from_user.id)
    
    response = f"🔥 Неформальный вариант:\n`{informal_text}`"
    if explanation:
        response += f"\n\n📚 Объяснение:\n{explanation}"
    
    await message.answer(response, parse_mode='Markdown', reply_markup=translation_mode_keyboard)