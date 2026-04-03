from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from utils.keyboards import cancel_keyboard, get_main_keyboard
from utils.states import SearchStates
from services.history_service import HistoryService
from services.search_service import SearchService

router = Router()

@router.callback_query(lambda c: c.data == "search_history")
async def start_search_history(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SearchStates.waiting_for_search)
    await state.update_data(search_type="history")
    await callback.message.answer(
        "🔍 Введите текст для поиска в истории:\n"
        "(для отмены нажмите ❌ Отменить)",
        reply_markup=cancel_keyboard
    )
    await callback.answer()

@router.message(SearchStates.waiting_for_search)
async def handle_search(message: types.Message, state: FSMContext, 
                       history_service: HistoryService, 
                       search_service: SearchService):
    if message.text == "❌ Отменить":
        await state.clear()
        await message.answer("✅ Поиск отменен", reply_markup=get_main_keyboard(message.from_user.id))
        return
    
    search_text = message.text
    data = await state.get_data()
    search_type = data.get('search_type', 'history')
    
    results = history_service.search_user_history(search_text, message.from_user.id)
    
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
    
    await show_search_results(message, state, search_service, 0)

async def show_search_results(message: types.Message, state: FSMContext, search_service: SearchService, offset: int = 0):
    data = await state.get_data()
    results = data.get('search_results', [])
    search_type = data.get('search_type', 'history')
    search_text = data.get('search_text', '')
    
    if not results:
        await message.answer("❌ Результаты поиска не найдены")
        return
    
    text = search_service.format_search_results(results, offset, search_type, search_text)
    reply_markup = search_service.create_search_results_keyboard(results, offset, search_type)
    
    if isinstance(message, CallbackQuery):
        await message.message.edit_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await message.answer(text, reply_markup=reply_markup, parse_mode='Markdown')
    
    await state.update_data(current_offset=offset)

@router.callback_query(lambda c: c.data.startswith('search_'))
async def handle_search_pagination(callback: CallbackQuery, state: FSMContext, search_service: SearchService):
    try:
        action, offset = callback.data.split('_')[1:]
        offset = int(offset)
        await show_search_results(callback, state, search_service, offset)
        await callback.answer()
    except Exception as e:
        await callback.answer("❌ Ошибка при загрузке")
        print(f"❌ Ошибка в handle_search_pagination: {e}")