import sqlite3
from typing import List, Dict, Tuple, Optional

class FDataBase:
    def __init__(self, db: sqlite3.Connection):
        self.__db = db
        self.__cur = self.__db.cursor()
        self._init_tables()

    def _init_tables(self):
        try:
            # Добавляем колонку explanation в таблицу translations если её нет
            self.__cur.execute("PRAGMA table_info(translations)")
            columns = [col[1] for col in self.__cur.fetchall()]
            
            if 'explanation' not in columns:
                self.__cur.execute('ALTER TABLE translations ADD COLUMN explanation TEXT')
                self.__db.commit()
                print("✅ Добавлена колонка explanation в таблицу translations")
                
        except sqlite3.Error as e:
            print(f"❌ Ошибка инициализации таблиц: {e}")

    def __del__(self):
        if hasattr(self, '__db'):
            self.__db.close()

    # Методы для истории переводов
    def add_translation(self, informal: str, formal: str, explanation: str = None, 
                       user_id: int = None, direction: str = "to_formal") -> bool:
        try:
            self.__cur.execute(
                'INSERT INTO translations (informal_text, formal_text, explanation, user_id, direction) VALUES (?, ?, ?, ?, ?)',
                (informal, formal, explanation, user_id, direction)
            )
            self.__db.commit()
            return True
        except sqlite3.Error as e:
            print(f"❌ Ошибка при добавлении перевода: {e}")
            return False
    
    def get_user_translations(self, user_id: int, limit: int = 1000) -> List[Dict]:
        try:
            self.__cur.execute('''
                SELECT * FROM translations 
                WHERE user_id = ?
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (user_id, limit))
        
            columns = [col[0] for col in self.__cur.description]
            return [dict(zip(columns, row)) for row in self.__cur.fetchall()]
        except sqlite3.Error as e:
            print(f"❌ Ошибка при получении переводов пользователя: {e}")
            return []
    
    def search_user_translations(self, search_text: str, user_id: int) -> List[Dict]:
        try:
            search_pattern = f'%{search_text}%'
            
            self.__cur.execute('''
                SELECT * FROM translations 
                WHERE (informal_text LIKE ? OR formal_text LIKE ?) AND user_id = ?
                ORDER BY created_at DESC
                LIMIT 20
            ''', (search_pattern, search_pattern, user_id))
            
            columns = [col[0] for col in self.__cur.description]
            return [dict(zip(columns, row)) for row in self.__cur.fetchall()]
        except sqlite3.Error as e:
            print(f"❌ Ошибка при поиске переводов пользователя: {e}")
            return []

    # Методы админ-панели
    def addAdmin(self, login: str, role: str):
        try:
            self.__cur.execute("INSERT INTO admins (login, role) VALUES (?, ?)", (login, role))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Failed to add admin:", str(e))

    def getAdminByLogin(self, login: str) -> str | None:
        try:
            self.__cur.execute("SELECT * FROM admins WHERE login=?", (login,))
            res = self.__cur.fetchone()
            if res: 
                return res[2]
        except sqlite3.Error as e:
            print("Failed to get admin role by login:", str(e))
        return None

    def getAdmin(self):
        try:
            self.__cur.execute("SELECT * FROM admins")
            res = self.__cur.fetchall()
            if res:
                return res
        except sqlite3.Error as e:
            print("Failed to get admins:", str(e))
        return []

    def removeAdminByID(self, AdminID: int):
        try:
            self.__cur.execute("DELETE FROM admins WHERE id=?", (AdminID,))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Failed to remove admin by id:", str(e))

    # Статистика
    def get_stats(self) -> Dict:
        try:
            self.__cur.execute('SELECT COUNT(*) FROM translations')
            total_translations = self.__cur.fetchone()[0]
            
            self.__cur.execute('SELECT COUNT(DISTINCT user_id) FROM translations')
            unique_users = self.__cur.fetchone()[0]
            
            self.__cur.execute('SELECT COUNT(*) FROM admins')
            total_admins = self.__cur.fetchone()[0]
            
            return {
                'total_translations': total_translations,
                'unique_users': unique_users,
                'total_admins': total_admins
            }
        except sqlite3.Error as e:
            print(f"❌ Ошибка получения статистики: {e}")
            return {}