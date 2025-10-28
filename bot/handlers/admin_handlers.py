from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from utils.keyboards import get_admin_keyboard, cancel_keyboard, dictionary_management_keyboard, role_selection_keyboard, get_main_keyboard
from utils.states import AdminStates
from services.admin_service import AdminService

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

@router.message(lambda message: message.text == "📝 Управление словарем")
async def dictionary_management_button(message: types.Message, admin_service: AdminService):
    if not admin_service.is_user_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав доступа")
        return
        
    await message.answer(
        "📝 Управление словарем:",
        reply_markup=dictionary_management_keyboard
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
        "Введите ID админа для удаления:\n"
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

@router.message(lambda message: message.text == "📊 Статистика")
async def show_admin_stats(message: Message, admin_service: AdminService):
    if not admin_service.is_user_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав доступа")
        return
        
    stats = admin_service.get_stats()
    
    text = (
        "📊 Статистика системы:\n\n"
        f"• 📖 Всего переводов: {stats.get('total_translations', 0)}\n"
        f"• 📚 Слов в словаре: {stats.get('total_words', 0)}\n"
        f"• 🔢 Всего использований: {stats.get('total_usage', 0)}"
    )
    
    await message.answer(text)