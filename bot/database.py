import sqlite3
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta

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
            # Добавляем отладочную информацию
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"🕐 Добавление перевода в {current_time}")
            
            self.__cur.execute(
                'INSERT INTO translations (informal_text, formal_text, explanation, user_id, direction) VALUES (?, ?, ?, ?, ?)',
                (informal, formal, explanation, user_id, direction)
            )
            self.__db.commit()
            
            # Проверяем добавленную запись
            self.__cur.execute('SELECT created_at FROM translations WHERE id = last_insert_rowid()')
            db_time = self.__cur.fetchone()[0]
            print(f"🕐 Время в базе данных: {db_time}")
            
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

    # Базовая статистика
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

    # Новые методы для расширенной статистики
    def get_detailed_stats(self) -> Dict:
        """Расширенная статистика системы"""
        try:
            # Базовая статистика
            self.__cur.execute('SELECT COUNT(*) FROM translations')
            total_translations = self.__cur.fetchone()[0]
            
            self.__cur.execute('SELECT COUNT(DISTINCT user_id) FROM translations')
            unique_users = self.__cur.fetchone()[0]
            
            self.__cur.execute('SELECT COUNT(*) FROM admins')
            total_admins = self.__cur.fetchone()[0]
            
            # Статистика по направлениям перевода
            self.__cur.execute('SELECT COUNT(*) FROM translations WHERE direction = "to_formal"')
            to_formal_count = self.__cur.fetchone()[0]
            
            self.__cur.execute('SELECT COUNT(*) FROM translations WHERE direction = "to_informal"')
            to_informal_count = self.__cur.fetchone()[0]
            
            # Активность за последние 7 дней
            week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
            self.__cur.execute('SELECT COUNT(*) FROM translations WHERE created_at > ?', (week_ago,))
            last_week_activity = self.__cur.fetchone()[0]
            
            # Самые активные пользователи
            self.__cur.execute('''
                SELECT user_id, COUNT(*) as translation_count 
                FROM translations 
                GROUP BY user_id 
                ORDER BY translation_count DESC 
                LIMIT 10
            ''')
            top_users = self.__cur.fetchall()
            
            # Статистика по дням (последние 7 дней)
            self.__cur.execute('''
                SELECT DATE(created_at) as day, COUNT(*) as count 
                FROM translations 
                WHERE created_at > ? 
                GROUP BY DATE(created_at) 
                ORDER BY day DESC
            ''', (week_ago,))
            daily_stats = self.__cur.fetchall()
            
            # Популярные слова для перевода (топ 10)
            self.__cur.execute('''
                SELECT informal_text, COUNT(*) as usage_count 
                FROM translations 
                GROUP BY informal_text 
                ORDER BY usage_count DESC 
                LIMIT 10
            ''')
            popular_words = self.__cur.fetchall()
            
            return {
                'total_translations': total_translations,
                'unique_users': unique_users,
                'total_admins': total_admins,
                'to_formal_count': to_formal_count,
                'to_informal_count': to_informal_count,
                'last_week_activity': last_week_activity,
                'top_users': top_users,
                'daily_stats': daily_stats,
                'popular_words': popular_words
            }
        except sqlite3.Error as e:
            print(f"❌ Ошибка получения детальной статистики: {e}")
            return {}
    
    def get_user_stats(self, user_id: int) -> Dict:
        """Статистика конкретного пользователя"""
        try:
            self.__cur.execute('SELECT COUNT(*) FROM translations WHERE user_id = ?', (user_id,))
            user_translations = self.__cur.fetchone()[0]
            
            self.__cur.execute('SELECT COUNT(*) FROM translations WHERE user_id = ? AND direction = "to_formal"', (user_id,))
            user_to_formal = self.__cur.fetchone()[0]
            
            self.__cur.execute('SELECT COUNT(*) FROM translations WHERE user_id = ? AND direction = "to_informal"', (user_id,))
            user_to_informal = self.__cur.fetchone()[0]
            
            # Последняя активность
            self.__cur.execute('SELECT MAX(created_at) FROM translations WHERE user_id = ?', (user_id,))
            last_activity = self.__cur.fetchone()[0]
            
            # Популярные слова пользователя
            self.__cur.execute('''
                SELECT informal_text, COUNT(*) as usage_count 
                FROM translations 
                WHERE user_id = ? 
                GROUP BY informal_text 
                ORDER BY usage_count DESC 
                LIMIT 5
            ''', (user_id,))
            user_popular_words = self.__cur.fetchall()
            
            return {
                'user_translations': user_translations,
                'user_to_formal': user_to_formal,
                'user_to_informal': user_to_informal,
                'last_activity': last_activity,
                'user_popular_words': user_popular_words
            }
        except sqlite3.Error as e:
            print(f"❌ Ошибка получения статистики пользователя: {e}")
            return {}
    
    def get_realtime_stats(self) -> Dict:
        try:
            # Получаем текущее время в UTC (как в базе данных)
            now_utc = datetime.utcnow()
            
            # Переводы за сегодня (используем UTC дату)
            today_utc = now_utc.strftime('%Y-%m-%d')
            self.__cur.execute('SELECT COUNT(*) FROM translations WHERE DATE(created_at) = ?', (today_utc,))
            today_translations = self.__cur.fetchone()[0]
            
            # Переводы за последний час (используем UTC время)
            hour_ago_utc = (now_utc - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
            self.__cur.execute('SELECT COUNT(*) FROM translations WHERE created_at > ?', (hour_ago_utc,))
            last_hour_activity = self.__cur.fetchone()[0]
            
            # Переводы за последние 15 минут
            fifteen_min_ago_utc = (now_utc - timedelta(minutes=15)).strftime('%Y-%m-%d %H:%M:%S')
            self.__cur.execute('SELECT COUNT(*) FROM translations WHERE created_at > ?', (fifteen_min_ago_utc,))
            last_15min_activity = self.__cur.fetchone()[0]
            
            # Активные пользователи сегодня
            self.__cur.execute('SELECT COUNT(DISTINCT user_id) FROM translations WHERE DATE(created_at) = ?', (today_utc,))
            active_users_today = self.__cur.fetchone()[0]
            
            return {
                'today_translations': today_translations,
                'last_hour_activity': last_hour_activity,
                'last_15min_activity': last_15min_activity,
                'active_users_today': active_users_today
            }
        except sqlite3.Error as e:
            print(f"❌ Ошибка получения реальной статистики: {e}")
            return {}