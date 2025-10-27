import sqlite3
from typing import List, Dict, Tuple, Optional

class FDataBase:
    def __init__(self, db: sqlite3.Connection):
        self.__db = db
        self.__cur = self.__db.cursor()
        self._init_tables()

    def _init_tables(self):
        try:
            self.__cur.execute("PRAGMA table_info(translations)")
            columns = [col[1] for col in self.__cur.fetchall()]
            
            if 'user_id' not in columns:
                self.__cur.execute('ALTER TABLE translations ADD COLUMN user_id INTEGER')
                self.__db.commit()
                print("✅ Добавлена колонка user_id в таблицу translations")
        except sqlite3.Error as e:
            print(f"❌ Ошибка инициализации таблиц: {e}")

    def __del__(self):
        self.__db.close()
    
    def add_translation(self, informal: str, formal: str, explanation: str = None, user_id: int = None) -> bool:
        try:
            self.__cur.execute(
                'SELECT id FROM translations WHERE informal_text = ? AND formal_text = ? AND user_id = ?',
                (informal, formal, user_id)
            )
            existing = self.__cur.fetchone()
            
            if existing:
                self.__cur.execute(
                    'UPDATE translations SET usage_count = usage_count + 1 WHERE id = ?',
                    (existing[0],)
                )
            else:
                self.__cur.execute(
                    'INSERT INTO translations (informal_text, formal_text, user_id) VALUES (?, ?, ?)',
                    (informal, formal, user_id)
                )
            
            self.__db.commit()
            return True
        except sqlite3.Error as e:
            print(f"❌ Ошибка при добавлении перевода: {e}")
            return False
    
    def get_user_translations(self, user_id: int, limit: int = 100) -> List[Dict]:
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
    
    def get_user_stats(self, user_id: int) -> Dict:
        try:
            self.__cur.execute('SELECT COUNT(*) FROM translations WHERE user_id = ?', (user_id,))
            user_translations = self.__cur.fetchone()[0]
            
            self.__cur.execute('SELECT SUM(usage_count) FROM translations WHERE user_id = ?', (user_id,))
            user_usage = self.__cur.fetchone()[0] or 0
            
            return {
                'user_translations': user_translations,
                'user_usage': user_usage
            }
        except sqlite3.Error as e:
            print(f"❌ Ошибка получения статистики пользователя: {e}")
            return {}

    def get_all_translations(self, limit: int = 100) -> List[Dict]:
        try:
            self.__cur.execute('''
                SELECT * FROM translations 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
            
            columns = [col[0] for col in self.__cur.description]
            return [dict(zip(columns, row)) for row in self.__cur.fetchall()]
        except sqlite3.Error as e:
            print(f"❌ Ошибка при получении переводов: {e}")
            return []
    
    def get_formal_translation(self, informal_text: str) -> Optional[Tuple[str, str]]:
        try:
            self.__cur.execute(
                'SELECT formal_text, explanation FROM words WHERE LOWER(informal_text) = LOWER(?)',
                (informal_text,)
            )
            result = self.__cur.fetchone()
            return (result[0], result[1]) if result else None
        except sqlite3.Error as e:
            print(f"❌ Ошибка поиска перевода: {e}")
            return None

    def get_informal_translation(self, formal_text: str) -> Optional[Tuple[str, str]]:
        try:
            self.__cur.execute(
                'SELECT informal_text, explanation FROM words WHERE LOWER(formal_text) = LOWER(?)',
                (formal_text,)
            )
            result = self.__cur.fetchone()
            return (result[0], result[1]) if result else None
        except sqlite3.Error as e:
            print(f"❌ Ошибка поиска обратного перевода: {e}")
            return None
    
    def search_translations(self, search_text: str) -> List[Dict]:
        try:
            search_pattern = f'%{search_text}%'
            self.__cur.execute('''
                SELECT * FROM translations 
                WHERE informal_text LIKE ? OR formal_text LIKE ?
                ORDER BY created_at DESC
                LIMIT 20
            ''', (search_pattern, search_pattern))
            
            columns = [col[0] for col in self.__cur.description]
            return [dict(zip(columns, row)) for row in self.__cur.fetchall()]
        except sqlite3.Error as e:
            print(f"❌ Ошибка при поиске: {e}")
            return []
    
    def get_dictionary(self, limit: int = 20) -> List[Dict]:
        try:
            self.__cur.execute('''
                SELECT * FROM words 
                ORDER BY informal_text
                LIMIT ?
            ''', (limit,))
            
            columns = [col[0] for col in self.__cur.description]
            return [dict(zip(columns, row)) for row in self.__cur.fetchall()]
        except sqlite3.Error as e:
            print(f"❌ Ошибка при получении словаря: {e}")
            return []
    
    def add_to_dictionary(self, informal: str, formal: str, explanation: str = '') -> bool:
        try:
            self.__cur.execute(
                'SELECT informal_text FROM words WHERE LOWER(informal_text) = LOWER(?)',
                (informal,)
            )
            existing = self.__cur.fetchone()
        
            if existing:
                self.__cur.execute(
                    'UPDATE words SET formal_text = ?, explanation = ? WHERE LOWER(informal_text) = LOWER(?)',
                    (formal, explanation, informal)
                )
            else:
                self.__cur.execute(
                    'INSERT INTO words (informal_text, formal_text, explanation) VALUES (?, ?, ?)',
                    (informal, formal, explanation)
                )
            
            self.__db.commit()
            return True
        except sqlite3.Error as e:
            print(f"❌ Ошибка добавления в словарь: {e}")
            return False
    
    def get_stats(self) -> Dict:
        try:
            self.__cur.execute('SELECT COUNT(*) FROM translations')
            total_translations = self.__cur.fetchone()[0]
            
            self.__cur.execute('SELECT COUNT(*) FROM words')
            total_words = self.__cur.fetchone()[0]
            
            self.__cur.execute('SELECT SUM(usage_count) FROM translations')
            total_usage = self.__cur.fetchone()[0] or 0
            
            return {
                'total_translations': total_translations,
                'total_words': total_words,
                'total_usage': total_usage
            }
        except sqlite3.Error as e:
            print(f"❌ Ошибка получения статистики: {e}")
            return {}

    def update_explanation(self, informal_text: str, explanation: str) -> bool:
        try:
            self.__cur.execute(
                'UPDATE words SET explanation = ? WHERE informal_text = ?',
                (explanation, informal_text)
            )
            self.__db.commit()
            return True
        except sqlite3.Error as e:
            print(f"❌ Ошибка обновления объяснения: {e}")
            return False

    def delete_translation(self, translation_id: int) -> bool:
        try:
            self.__cur.execute('DELETE FROM translations WHERE id = ?', (translation_id,))
            self.__db.commit()
            return True
        except sqlite3.Error as e:
            print(f"❌ Ошибка удаления: {e}")
            return False

    def addAdmin(self, login, role: bool):
        if (bool(role)):
            role = "GreatAdmin"
        else:
            role = "admin"
        try:
            self.__cur.execute("INSERT INTO admins (login, role) VALUES (?, ?)", (login, role))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Failed to add admin:", str(e))

    def getAdminByLogin(self, login) -> str | None:
        try:
            self.__cur.execute("SELECT * FROM admins WHERE login=?", (login,))
            res = self.__cur.fetchone()
            if res: return res[2]
        except sqlite3.Error as e:
            print("Failed to get admin role by login:", str(e))
        return None

    def removeAdminByLogin(self, login):
        try:
            self.__cur.execute("DELETE FROM admins WHERE login=? and role='admin'", (login,))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Failed to remove admin by login:", str(e))

    def getAdmin(self):
        try:
            self.__cur.execute("SELECT * FROM admins")
            res = self.__cur.fetchall()
            if res:
                return res
        except sqlite3.Error as e:
            print("Failed to get admins:", str(e))
        return []

    def getAdminByID(self, id):
        try:
            self.__cur.execute("SELECT * FROM admins WHERE id = ?", (id,))
            res = self.__cur.fetchone()
            if res: return res
        except sqlite3.Error as e:
            print("Failed to get admin by id:", str(e))
        return {}

    def removeAdminByID(self, AdminID):
        try:
            self.__cur.execute("DELETE FROM admins WHERE id=?", (AdminID,))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Failed to remove admin by id:", str(e))

    def updateAdmin(self, adminID, role):
        adm = self.getAdminByID(adminID)
        role = adm[2] if role is None else role
        
        try:
            self.__cur.execute("UPDATE admins SET role=? WHERE id=?", (role, adminID))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Failed to update adm data by id:", str(e))
