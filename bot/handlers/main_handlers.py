from aiogram import Router, types
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from utils.keyboards import get_main_keyboard

router = Router()

@router.message(CommandStart())
async def start_command(message: types.Message):
    user_id = message.from_user.id
    await message.answer(
        f"👋 Привет! Я бот для перевода между формальным и неформальным стилем.\n\n"
        f"🆔 Ваш Telegram ID: `{user_id}`\n\n"
        f"🤖 Переводчик: GigaChat Neural Network\n"
        f"🌐 Для веб-версии используйте этот ID\n"
        f"📝 Используй кнопки для навигации!",
        reply_markup=get_main_keyboard(message.from_user.id),
        parse_mode='Markdown'
    )

@router.message(lambda message: message.text == "⬅️ Назад в меню")
async def go_back_to_main_menu(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Главное меню:",
        reply_markup=get_main_keyboard(message.from_user.id)
    )