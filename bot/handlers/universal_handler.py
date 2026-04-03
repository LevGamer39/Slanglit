from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from utils.keyboards import get_main_keyboard, translation_mode_keyboard
from utils.states import TranslationStates, SearchStates, AdminStates
from services.translation_service import TranslationService
from services.admin_service import AdminService

router = Router()

@router.message()
async def handle_any_message(message: Message, state: FSMContext, translation_service: TranslationService, admin_service: AdminService):
    # Обработка не текстовых сообщений (стикеры, GIF, фото, видео и т.д.)
    if message.content_type != 'text':
        current_state = await state.get_state()
        
        # Если находимся в режиме перевода - показываем ошибку
        if current_state in [TranslationStates.waiting_for_informal.state, 
                           TranslationStates.waiting_for_formal.state]:
            await message.answer("❌ В режиме перевода поддерживаются только текстовые сообщения", reply_markup=translation_mode_keyboard)
            return
        
        # Если находимся в других состояниях, где ожидается текст
        text_input_states = [
            SearchStates.waiting_for_search.state,
            AdminStates.waiting_for_admin_login.state,
            AdminStates.waiting_for_admin_role.state,
            AdminStates.waiting_for_admin_remove.state,
        ]
        
        if current_state in text_input_states:
            await message.answer("❌ В этом режиме поддерживаются только текстовые сообщения")
            return
        
        # Если не в активном состоянии - показываем общее сообщение и возвращаем в главное меню
        response_text = (
            "❌ Поддерживаются только текстовые сообщения\n\n"
            "📝 Пожалуйста, используйте кнопки меню для выбора действия:\n"
            "• 🔄 Перевод - для перевода текста\n"
            "• 📖 История - для просмотра истории переводов\n"
        )
        
        # Добавляем админ-панель только если пользователь админ
        if admin_service.is_user_admin(message.from_user.id):
            response_text += "• ⚙️ Админ-панель - для управления\n"
        
        await message.answer(
            response_text,
            reply_markup=get_main_keyboard(message.from_user.id)
        )
        return
    
    # Дальше обрабатываем только текстовые сообщения
    
    # Системные кнопки и команды - пропускаем (их обработают другие хендлеры)
    system_buttons = [
        "🔄 Перевод", "📖 История", "⚙️ Админ-панель",
        "💼 Неформальный → Формальный", "🔥 Формальный → Неформальный",
        "❌ Выйти из режима перевода", "⬅️ Назад в меню",
        "👥 Список админов", "➕ Добавить админа", "➖ Удалить админа",
        "📊 Статистика", "⬅️ Назад в админ-панель",
        "❌ Отменить", "✅ Да, удалить", "❌ Нет, отменить", 
        "👑 GreatAdmin", "👤 Admin"
    ]
    
    if message.text in system_buttons or message.text.startswith('/'):
        return
    
    current_state = await state.get_state()
    
    # Если находимся в состоянии перевода - автоматически переводим
    if current_state:
        if len(message.text.strip()) < 1:
            await message.answer("❌ Введите текст для перевода")
            return
        
        try:
            if current_state == TranslationStates.waiting_for_informal.state:
                user_text = message.text
                formal_text, explanation = translation_service.translate_to_formal(user_text, message.from_user.id)
                
                response = f"💼 Формальный вариант:\n`{formal_text}`"
                if explanation:
                    response += f"\n\n📚 Объяснение:\n{explanation}"
                
                await message.answer(response, parse_mode='Markdown', reply_markup=translation_mode_keyboard)
                
            elif current_state == TranslationStates.waiting_for_formal.state:
                user_text = message.text
                informal_text, explanation = translation_service.translate_to_informal(user_text, message.from_user.id)
                
                response = f"🔥 Неформальный вариант:\n`{informal_text}`"
                if explanation:
                    response += f"\n\n📚 Объяснение:\n{explanation}"
                
                await message.answer(response, parse_mode='Markdown', reply_markup=translation_mode_keyboard)
                
            else:
                # Для других состояний ничего не делаем - их обработают специализированные хендлеры
                return
                
        except Exception as e:
            await message.answer("❌ Произошла ошибка при обработке сообщения")
            print(f"❌ Ошибка в handle_any_message: {e}")
    
    else:
        # Если не в состоянии и не системная кнопка - показываем сообщение о выборе режима и возвращаем в главное меню
        response_text = (
            "❌ Вы не выбрали режим работы.\n\n"
            "📝 Пожалуйста, используйте кнопки меню для выбора действия:\n"
            "• 🔄 Перевод - для перевода текста\n"
            "• 📖 История - для просмотра истории переводов\n"
        )
        
        # Добавляем админ-панель только если пользователь админ
        if admin_service.is_user_admin(message.from_user.id):
            response_text += "• ⚙️ Админ-панель - для управления\n"
        
        await message.answer(
            response_text,
            reply_markup=get_main_keyboard(message.from_user.id)
        )