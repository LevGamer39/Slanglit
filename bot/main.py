from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import sqlite3
from database import FDataBase

from config import BOT_TOKEN
from handlers.main_handlers import router as main_router
from handlers.translation_handlers import router as translation_router
from handlers.admin_handlers import router as admin_router
from handlers.history_handlers import router as history_router
from handlers.search_handlers import router as search_router
from handlers.universal_handler import router as universal_router

from services.translation_service import TranslationService
from services.admin_service import AdminService
from services.history_service import HistoryService
from services.search_service import SearchService

def connect_db():
    return sqlite3.connect('translations.db')

async def main():
    # Инициализация базы данных
    db_connection = connect_db()
    db = FDataBase(db_connection)
    
    # Инициализация сервисов
    translation_service = TranslationService(db)
    admin_service = AdminService(db)
    history_service = HistoryService(db)
    search_service = SearchService()
    
    # Инициализация бота
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Регистрация сервисов в диспетчере
    dp['translation_service'] = translation_service
    dp['admin_service'] = admin_service
    dp['history_service'] = history_service
    dp['search_service'] = search_service
    dp['db'] = db
    
    # Регистрация роутеров
    dp.include_router(main_router)
    dp.include_router(translation_router)
    dp.include_router(admin_router)
    dp.include_router(history_router)
    dp.include_router(search_router)
    dp.include_router(universal_router)
    
    print("✅ Бот запущен с нейросетью GigaChat!")
    print("✅ База данных: translations.db")
    print("🤖 Переводчик: GigaChat API")
    print("📝 Просто пишите сообщения - они автоматически сохранятся в историю!")
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())