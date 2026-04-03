from .main_handlers import router as main_router
from .translation_handlers import router as translation_router
from .admin_handlers import router as admin_router
from .history_handlers import router as history_router
from .search_handlers import router as search_router
from .universal_handler import router as universal_router

__all__ = [
    'main_router', 
    'translation_router', 
    'admin_router', 
    'history_router', 
    'search_router',
    'universal_router'
]