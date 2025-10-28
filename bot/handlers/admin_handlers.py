from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from utils.keyboards import get_admin_keyboard, cancel_keyboard, role_selection_keyboard, get_main_keyboard, get_stats_keyboard, get_user_stats_keyboard
from utils.states import AdminStates, StatsStates
from services.admin_service import AdminService
from datetime import datetime

router = Router()

@router.message(lambda message: message.text == "⚙️ Админ-панель")
async def admin_panel_button(message: types.Message, admin_service: AdminService):
    if not admin_service.is_user_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав доступа к админ-панели")
        return
    
    admin_role = admin_service.get_admin_role(message.from_user.id)
    await message.answer(
        f"⚙️ Админ-панель (Ваша роль: {admin_role})\n\n"
        "Выберите действие:",
        reply_markup=get_admin_keyboard(admin_role)
    )

@router.message(lambda message: message.text == "⬅️ Назад в админ-панель")
async def back_to_admin_panel(message: types.Message, admin_service: AdminService):
    if not admin_service.is_user_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав доступа")
        return
        
    admin_role = admin_service.get_admin_role(message.from_user.id)
    await message.answer(
        f"⚙️ Админ-панель (Ваша роль: {admin_role})\n\n"
        "Выберите действие:",
        reply_markup=get_admin_keyboard(admin_role)
    )

@router.message(lambda message: message.text == "👥 Список админов")
async def show_admins(message: Message, admin_service: AdminService):
    if not admin_service.is_user_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав доступа")
        return
        
    admins = admin_service.get_admins_list()
    
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

@router.message(lambda message: message.text == "➕ Добавить админа")
async def add_admin_start(message: Message, state: FSMContext, admin_service: AdminService):
    if not admin_service.is_user_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав доступа")
        return
    
    admin_role = admin_service.get_admin_role(message.from_user.id)
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

@router.message(AdminStates.waiting_for_admin_login)
async def add_admin_login(message: Message, state: FSMContext, admin_service: AdminService):
    if message.text == "❌ Отменить":
        await state.clear()
        admin_role = admin_service.get_admin_role(message.from_user.id)
        await message.answer("✅ Добавление админа отменено", reply_markup=get_admin_keyboard(admin_role))
        return
    
    if not message.text.isdigit():
        await message.answer("❌ Введите корректный числовой ID пользователя")
        return
    
    await state.update_data(admin_login=message.text)
    await state.set_state(AdminStates.waiting_for_admin_role)
    
    await message.answer(
        "Выберите роль админа:",
        reply_markup=role_selection_keyboard
    )

@router.message(AdminStates.waiting_for_admin_role)
async def add_admin_role(message: Message, state: FSMContext, admin_service: AdminService):
    if message.text == "❌ Отменить":
        await state.clear()
        admin_role = admin_service.get_admin_role(message.from_user.id)
        await message.answer("✅ Добавление админа отменено", reply_markup=get_admin_keyboard(admin_role))
        return
    
    role_map = {"👑 GreatAdmin": "GreatAdmin", "👤 Admin": "Admin"}
    if message.text not in role_map:
        await message.answer("❌ Пожалуйста, выберите роль из предложенных вариантов")
        return
    
    data = await state.get_data()
    admin_login = data['admin_login']
    
    success = admin_service.add_admin(admin_login, role_map[message.text])
    
    if success:
        admin_role = admin_service.get_admin_role(message.from_user.id)
        await message.answer(f"✅ Пользователь с ID {admin_login} добавлен как админ", reply_markup=get_admin_keyboard(admin_role))
    else:
        await message.answer("❌ Ошибка при добавлении админа")
    
    await state.clear()

@router.message(lambda message: message.text == "➖ Удалить админа")
async def remove_admin_start(message: Message, state: FSMContext, admin_service: AdminService):
    if not admin_service.is_user_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав доступа")
        return
    
    admin_role = admin_service.get_admin_role(message.from_user.id)
    if admin_role != "GreatAdmin":
        await message.answer("❌ Только GreatAdmin может удалять админов", reply_markup=get_admin_keyboard(admin_role))
        return
        
    await state.set_state(AdminStates.waiting_for_admin_remove)
    await message.answer(
        "Введите ID админа (из списка админов) для удаления:\n"
        "(для отмены нажмите ❌ Отменить)",
        reply_markup=cancel_keyboard
    )

@router.message(AdminStates.waiting_for_admin_remove)
async def remove_admin_execute(message: Message, state: FSMContext, admin_service: AdminService):
    if message.text == "❌ Отменить":
        await state.clear()
        admin_role = admin_service.get_admin_role(message.from_user.id)
        await message.answer("✅ Удаление админа отменено", reply_markup=get_admin_keyboard(admin_role))
        return
    
    try:
        admin_id = int(message.text)
        success = admin_service.remove_admin(admin_id)
        
        if success:
            admin_role = admin_service.get_admin_role(message.from_user.id)
            await message.answer(f"✅ Админ с ID {admin_id} удален", reply_markup=get_admin_keyboard(admin_role))
        else:
            await message.answer("❌ Ошибка при удалении админа")
            
    except ValueError:
        await message.answer("❌ Введите корректный ID (число)")
        return
    
    await state.clear()

@router.message(lambda message: message.text == "📊 Базовая статистика")
async def show_basic_stats(message: Message, admin_service: AdminService):
    if not admin_service.is_user_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав доступа")
        return
        
    stats = admin_service.get_stats()
    
    text = (
        "📊 Базовая статистика системы:\n\n"
        f"• 📖 Всего переводов: {stats.get('total_translations', 0)}\n"
        f"• 👥 Уникальных пользователей: {stats.get('unique_users', 0)}\n"
        f"• 👮 Администраторов: {stats.get('total_admins', 0)}\n\n"
        "🤖 Переводчик: GigaChat Neural Network"
    )
    
    await message.answer(text, reply_markup=get_stats_keyboard())

@router.message(lambda message: message.text == "📈 Детальная статистика")
async def show_detailed_stats(message: Message, admin_service: AdminService):
    if not admin_service.is_user_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав доступа")
        return
        
    stats = admin_service.get_detailed_stats()
    
    text = "📈 Детальная статистика системы:\n\n"
    text += f"• 📊 Всего переводов: {stats.get('total_translations', 0)}\n"
    text += f"• 👥 Уникальных пользователей: {stats.get('unique_users', 0)}\n"
    text += f"• 💼 → Формальных: {stats.get('to_formal_count', 0)}\n"
    text += f"• 🔥 → Неформальных: {stats.get('to_informal_count', 0)}\n"
    text += f"• 📅 Активность за 7 дней: {stats.get('last_week_activity', 0)}\n\n"
    
    # Топ пользователей
    top_users = stats.get('top_users', [])
    if top_users:
        text += "🏆 Топ пользователей:\n"
        for i, (user_id, count) in enumerate(top_users[:5], 1):
            text += f"{i}. ID {user_id}: {count} переводов\n"
    
    # Популярные слова
    popular_words = stats.get('popular_words', [])
    if popular_words:
        text += "\n🔥 Популярные слова:\n"
        for i, (word, count) in enumerate(popular_words[:5], 1):
            text += f"{i}. '{word}': {count} раз\n"
    
    await message.answer(text, reply_markup=get_stats_keyboard())

@router.message(lambda message: message.text == "👤 Статистика пользователей")
async def show_user_stats_menu(message: Message):
    await message.answer(
        "👤 Статистика пользователей:\n\n"
        "Выберите действие:",
        reply_markup=get_user_stats_keyboard()
    )

@router.message(lambda message: message.text == "👤 Топ пользователей")
async def show_top_users(message: Message, admin_service: AdminService):
    if not admin_service.is_user_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав доступа")
        return
        
    stats = admin_service.get_detailed_stats()
    top_users = stats.get('top_users', [])
    
    if not top_users:
        await message.answer("📭 Нет данных о пользователях")
        return
    
    text = "🏆 Топ самых активных пользователей:\n\n"
    for i, (user_id, count) in enumerate(top_users, 1):
        user_stats = admin_service.get_user_stats(user_id)
        text += f"{i}. 👤 ID: {user_id}\n"
        text += f"   📊 Переводов: {count}\n"
        text += f"   💼 → Формальных: {user_stats.get('user_to_formal', 0)}\n"
        text += f"   🔥 → Неформальных: {user_stats.get('user_to_informal', 0)}\n"
        
        if user_stats.get('last_activity'):
            text += f"   🕐 Последняя активность: {user_stats['last_activity'][:16]}\n"
        
        text += "\n"
    
    await message.answer(text, reply_markup=get_user_stats_keyboard())

@router.message(lambda message: message.text == "🔍 Поиск пользователя")
async def search_user_start(message: Message, state: FSMContext, admin_service: AdminService):
    if not admin_service.is_user_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав доступа")
        return
        
    await state.set_state(StatsStates.waiting_for_user_search)
    await message.answer(
        "Введите ID пользователя для просмотра статистики:\n"
        "(для отмены нажмите ❌ Отменить)",
        reply_markup=cancel_keyboard
    )

@router.message(StatsStates.waiting_for_user_search)
async def show_user_stats(message: Message, state: FSMContext, admin_service: AdminService):
    if message.text == "❌ Отменить":
        await state.clear()
        await message.answer("✅ Поиск отменен", reply_markup=get_user_stats_keyboard())
        return
    
    if not message.text.isdigit():
        await message.answer("❌ Введите корректный числовой ID пользователя")
        return
    
    user_id = int(message.text)
    user_stats = admin_service.get_user_stats(user_id)
    
    if user_stats['user_translations'] == 0:
        await message.answer(f"❌ Пользователь с ID {user_id} не найден или не имеет переводов")
        return
    
    text = f"👤 Статистика пользователя ID: {user_id}\n\n"
    text += f"📊 Всего переводов: {user_stats['user_translations']}\n"
    text += f"💼 → Формальных: {user_stats['user_to_formal']}\n"
    text += f"🔥 → Неформальных: {user_stats['user_to_informal']}\n"
    
    if user_stats.get('last_activity'):
        text += f"🕐 Последняя активность: {user_stats['last_activity'][:16]}\n"
    
    # Популярные слова пользователя
    popular_words = user_stats.get('user_popular_words', [])
    if popular_words:
        text += "\n🔥 Часто переводимые слова:\n"
        for i, (word, count) in enumerate(popular_words, 1):
            text += f"{i}. '{word}': {count} раз\n"
    
    await state.clear()
    await message.answer(text, reply_markup=get_user_stats_keyboard())

@router.message(lambda message: message.text == "🕐 Активность в реальном времени")
async def show_realtime_stats(message: Message, admin_service: AdminService):
    if not admin_service.is_user_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав доступа")
        return
        
    stats = admin_service.get_realtime_stats()
    detailed_stats = admin_service.get_detailed_stats()
    
    text = "🕐 Активность в реальном времени:\n\n"
    text += f"• 📊 Переводов сегодня: {stats.get('today_translations', 0)}\n"
    text += f"• ⏰ Переводов за последний час: {stats.get('last_hour_activity', 0)}\n"
    text += f"• ⚡ Переводов за последние 15 минут: {stats.get('last_15min_activity', 0)}\n"
    text += f"• 👥 Активных пользователей сегодня: {stats.get('active_users_today', 0)}\n\n"
    
    # Активность по дням
    daily_stats = detailed_stats.get('daily_stats', [])
    if daily_stats:
        text += "📅 Активность по дням:\n"
        for day, count in daily_stats[:7]:  # Последние 7 дней
            text += f"• {day}: {count} переводов\n"
    
    await message.answer(text, reply_markup=get_stats_keyboard())

@router.message(lambda message: message.text in ["⬅️ Назад к статистике", "⬅️ Назад в админ-панель"])
async def back_to_stats(message: Message, admin_service: AdminService):
    if not admin_service.is_user_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав доступа")
        return
        
    admin_role = admin_service.get_admin_role(message.from_user.id)
    if message.text == "⬅️ Назад в админ-панель":
        await message.answer(
            f"⚙️ Админ-панель (Ваша роль: {admin_role})\n\n"
            "Выберите действие:",
            reply_markup=get_admin_keyboard(admin_role)
        )
    else:
        await message.answer(
            "📊 Статистика системы:\n\n"
            "Выберите тип статистики:",
            reply_markup=get_stats_keyboard()
        )