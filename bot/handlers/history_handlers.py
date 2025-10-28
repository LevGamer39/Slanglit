from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from services.history_service import HistoryService

router = Router()

@router.message(lambda message: message.text == "📖 История")
async def history_button(message: types.Message, history_service: HistoryService):
    await show_history(message, history_service)

async def show_history(message: types.Message, history_service: HistoryService, offset: int = 0):
    translations = history_service.get_user_history(message.from_user.id, 1000)
    
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
            text += f"{i}. 💼 Неформальный → Формальный\n"
            text += f"   🔥 `{trans['informal_text']}`\n"
            text += f"   → 💼 `{trans['formal_text']}`\n"
        else:
            text += f"{i}. 🔥 Формальный → Неформальный\n"
            text += f"   💼 `{trans['informal_text']}`\n"
            text += f"   → 🔥 `{trans['formal_text']}`\n"
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

@router.callback_query(lambda c: c.data.startswith('history_'))
async def handle_history_pagination(callback: CallbackQuery, history_service: HistoryService):
    try:
        action, offset = callback.data.split('_')[1:]
        offset = int(offset)
        await show_history(callback, history_service, offset)
        await callback.answer()
    except Exception as e:
        await callback.answer("❌ Ошибка при загрузке")
        print(f"❌ Ошибка в handle_history_pagination: {e}")