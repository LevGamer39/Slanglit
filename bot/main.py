from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import sqlite3
from database import FDataBase

from config import BOT_TOKEN
from handlers.main_handlers import router as main_router
from handlers.translation_handlers import router as translation_router
from handlers.admin_handlers import router as admin_router
from handlers.dictionary_handlers import router as dictionary_router
from handlers.history_handlers import router as history_router
from handlers.search_handlers import router as search_router
from handlers.universal_handler import router as universal_router

from services.translation_service import TranslationService
from services.admin_service import AdminService
from services.dictionary_service import DictionaryService
from services.history_service import HistoryService
from services.search_service import SearchService
from services.profanity_service import ProfanityService

def connect_db():
    return sqlite3.connect('translations.db')

async def main():
    # Инициализация базы данных
    db_connection = connect_db()
    db = FDataBase(db_connection)
    
    # Инициализация сервисов - ВАЖНО: сначала создаем profanity_service
    profanity_service = ProfanityService(db)
    translation_service = TranslationService(db, profanity_service)  # Теперь передаем profanity_service
    admin_service = AdminService(db)
    dictionary_service = DictionaryService(db)
    history_service = HistoryService(db)
    search_service = SearchService()
    
    # Инициализация бота
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Регистрация сервисов в диспетчере
    dp['translation_service'] = translation_service
    dp['admin_service'] = admin_service
    dp['dictionary_service'] = dictionary_service
    dp['history_service'] = history_service
    dp['search_service'] = search_service
    dp['profanity_service'] = profanity_service  # Регистрируем profanity_service отдельно
    dp['db'] = db
    
    # Регистрация роутеров
    dp.include_router(main_router)
    dp.include_router(translation_router)
    dp.include_router(admin_router)
    dp.include_router(dictionary_router)
    dp.include_router(history_router)
    dp.include_router(search_router)
    dp.include_router(universal_router)  # ← Этот должен быть последним!
    
    print("✅ Бот запущен!")
    print("✅ База данных: translations.db")
    print("✅ Система проверки матов активирована")
    print("📝 Просто пишите сообщения - они автоматически сохранятся!")
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())