from aiogram import Router, types
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from utils.keyboards import get_main_keyboard

router = Router()

@router.message(CommandStart())
async def start_command(message: types.Message):
    await message.answer(
        "👋 Привет! Я бот для перевода между формальным и неформальным стилем.\n\n"
        "🤖 Переводчик: GigaChat Neural Network\n"
        "📝 Используй кнопки для навигации!",
        reply_markup=get_main_keyboard(message.from_user.id)
    )

@router.message(lambda message: message.text == "⬅️ Назад в меню")
async def go_back_to_main_menu(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Главное меню:",
        reply_markup=get_main_keyboard(message.from_user.id)
    )