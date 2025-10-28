import sqlite3
from database import FDataBase
from typing import Dict, List

def connect_db():
    return sqlite3.connect('translations.db')

class AdminService:
    def __init__(self, db: FDataBase):
        self.db = db

    def is_user_admin(self, user_id: int) -> bool:
        admin_role = self.db.getAdminByLogin(str(user_id))
        return admin_role in ["GreatAdmin", "Admin"]

    def get_admin_role(self, user_id: int) -> str:
        return self.db.getAdminByLogin(str(user_id))

    def get_admins_list(self):
        return self.db.getAdmin()

    def add_admin(self, login: str, role: str) -> bool:
        try:
            self.db.addAdmin(login, role)
            return True
        except Exception as e:
            print(f"Error adding admin: {e}")
            return False

    def remove_admin(self, admin_id: int) -> bool:
        try:
            self.db.removeAdminByID(admin_id)
            return True
        except Exception as e:
            print(f"Error removing admin: {e}")
            return False

    def get_stats(self):
        return self.db.get_stats()
    
    # Новые методы для расширенной статистики
    def get_detailed_stats(self) -> Dict:
        """Расширенная статистика системы"""
        return self.db.get_detailed_stats()
    
    def get_user_stats(self, user_id: int) -> Dict:
        """Статистика конкретного пользователя"""
        return self.db.get_user_stats(user_id)
    
    def get_realtime_stats(self) -> Dict:
        """Статистика в реальном времени"""
        return self.db.get_realtime_stats()
    
    def search_users(self, search_query: str = "") -> List:
        """Поиск пользователей по активности"""
        try:
            # Здесь можно добавить логику поиска пользователей
            # Пока возвращаем топ пользователей
            stats = self.db.get_detailed_stats()
            return stats.get('top_users', [])
        except Exception as e:
            print(f"Error searching users: {e}")
            return []