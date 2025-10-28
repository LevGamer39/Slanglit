import sqlite3
from typing import List, Dict, Tuple, Optional
import json

class FDataBase:
    def __init__(self, db: sqlite3.Connection):
        self.__db = db
        self.__cur = self.__db.cursor()
        self._init_tables()

    def _init_tables(self):
        try:
            # Проверяем и добавляем недостающие колонки в translations
            self.__cur.execute("PRAGMA table_info(translations)")
            columns = [col[1] for col in self.__cur.fetchall()]
            
            if 'user_id' not in columns:
                self.__cur.execute('ALTER TABLE translations ADD COLUMN user_id INTEGER')
                self.__db.commit()
                print("✅ Добавлена колонка user_id в таблицу translations")
            
            if 'direction' not in columns:
                self.__cur.execute('ALTER TABLE translations ADD COLUMN direction TEXT DEFAULT "to_formal"')
                self.__db.commit()
                print("✅ Добавлена колонка direction в таблицу translations")
                
            # Создаем таблицу для матных слов если её нет
            self.__cur.execute('''
                CREATE TABLE IF NOT EXISTS profanity_words (
                    word TEXT PRIMARY KEY NOT NULL
                )
            ''')
            self.__db.commit()
            print("✅ Таблица profanity_words создана/проверена")
                
        except sqlite3.Error as e:
            print(f"❌ Ошибка инициализации таблиц: {e}")

    def __del__(self):
        self.__db.close()

#pragma region Translation Methods
    def add_translation(self, informal: str, formal: str, explanation: str = None, user_id: int = None, direction: str = "to_formal") -> bool:
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
                    'INSERT INTO translations (informal_text, formal_text, user_id, direction) VALUES (?, ?, ?, ?)',
                    (informal, formal, user_id, direction)
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
            # Приводим все к нижнему регистру для поиска
            search_lower = search_text.lower()
            search_pattern = f'%{search_lower}%'
            
            self.__cur.execute('''
                SELECT * FROM translations 
                WHERE (LOWER(informal_text) LIKE ? OR LOWER(formal_text) LIKE ?) AND user_id = ?
                ORDER BY created_at DESC
                LIMIT 20
            ''', (search_pattern, search_pattern, user_id))
            
            columns = [col[0] for col in self.__cur.description]
            return [dict(zip(columns, row)) for row in self.__cur.fetchall()]
        except sqlite3.Error as e:
            print(f"❌ Ошибка при поиске переводов пользователя: {e}")
            return []
#pragma endregion

#pragma region Dictionary Methods
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
    
    def get_dictionary(self, limit: int = 20, offset: int = 0) -> List[Dict]:
        try:
            self.__cur.execute('''
                SELECT * FROM words 
                ORDER BY informal_text
                LIMIT ? OFFSET ?
            ''', (limit, offset))
            
            columns = [col[0] for col in self.__cur.description]
            return [dict(zip(columns, row)) for row in self.__cur.fetchall()]
        except sqlite3.Error as e:
            print(f"❌ Ошибка при получении словаря: {e}")
            return []
    
    def get_dictionary_count(self) -> int:
        try:
            self.__cur.execute('SELECT COUNT(*) FROM words')
            return self.__cur.fetchone()[0]
        except sqlite3.Error as e:
            print(f"❌ Ошибка при подсчете слов в словаре: {e}")
            return 0
    
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
    
    def delete_from_dictionary(self, informal_text: str) -> bool:
        try:
            self.__cur.execute('DELETE FROM words WHERE informal_text = ?', (informal_text,))
            self.__db.commit()
            return True
        except sqlite3.Error as e:
            print(f"❌ Ошибка удаления из словаря: {e}")
            return False
    
    def get_word_by_informal(self, informal_text: str) -> Optional[Dict]:
        try:
            self.__cur.execute('SELECT * FROM words WHERE informal_text = ?', (informal_text,))
            columns = [col[0] for col in self.__cur.description]
            row = self.__cur.fetchone()
            return dict(zip(columns, row)) if row else None
        except sqlite3.Error as e:
            print(f"❌ Ошибка получения слова: {e}")
            return None
    
    def search_dictionary(self, search_text: str) -> List[Dict]:
        try:
            # Приводим все к нижнему регистру для поиска
            search_lower = search_text.lower()
            search_pattern = f'%{search_lower}%'
            
            self.__cur.execute('''
                SELECT * FROM words 
                WHERE LOWER(informal_text) LIKE ? OR 
                      LOWER(formal_text) LIKE ? OR 
                      LOWER(explanation) LIKE ?
                ORDER BY informal_text
                LIMIT 20
            ''', (search_pattern, search_pattern, search_pattern))
            
            columns = [col[0] for col in self.__cur.description]
            return [dict(zip(columns, row)) for row in self.__cur.fetchall()]
        except sqlite3.Error as e:
            print(f"❌ Ошибка при поиске в словаре: {e}")
            return []

#pragma region Alphabet Navigation Methods
    def get_words_by_letter(self, letter: str, limit: int = 50, offset: int = 0) -> List[Dict]:
        """Получить слова на определенную букву"""
        try:
            if letter == '0-9':
                # Для цифр и символов
                self.__cur.execute('''
                    SELECT * FROM words 
                    WHERE (
                        informal_text LIKE '0%' OR informal_text LIKE '1%' OR 
                        informal_text LIKE '2%' OR informal_text LIKE '3%' OR 
                        informal_text LIKE '4%' OR informal_text LIKE '5%' OR 
                        informal_text LIKE '6%' OR informal_text LIKE '7%' OR 
                        informal_text LIKE '8%' OR informal_text LIKE '9%'
                    )
                    ORDER BY informal_text 
                    LIMIT ? OFFSET ?
                ''', (limit, offset))
            elif letter == 'ALL':
                # Все слова
                self.__cur.execute('''
                    SELECT * FROM words 
                    ORDER BY informal_text 
                    LIMIT ? OFFSET ?
                ''', (limit, offset))
            else:
                # Для букв - ищем и в верхнем и в нижнем регистре
                self.__cur.execute('''
                    SELECT * FROM words 
                    WHERE UPPER(SUBSTR(informal_text, 1, 1)) = ? OR LOWER(SUBSTR(informal_text, 1, 1)) = ?
                    ORDER BY informal_text 
                    LIMIT ? OFFSET ?
                ''', (letter, letter.lower(), limit, offset))
            
            columns = [col[0] for col in self.__cur.description]
            return [dict(zip(columns, row)) for row in self.__cur.fetchall()]
        except sqlite3.Error as e:
            print(f"❌ Ошибка получения слов по букве {letter}: {e}")
            return []

    def get_words_count_by_letter(self, letter: str) -> int:
        """Получить количество слов на букву"""
        try:
            if letter == '0-9':
                self.__cur.execute('''
                    SELECT COUNT(*) FROM words 
                    WHERE (
                        informal_text LIKE '0%' OR informal_text LIKE '1%' OR 
                        informal_text LIKE '2%' OR informal_text LIKE '3%' OR 
                        informal_text LIKE '4%' OR informal_text LIKE '5%' OR 
                        informal_text LIKE '6%' OR informal_text LIKE '7%' OR 
                        informal_text LIKE '8%' OR informal_text LIKE '9%'
                    )
                ''')
            elif letter == 'ALL':
                self.__cur.execute('SELECT COUNT(*) FROM words')
            else:
                self.__cur.execute('''
                    SELECT COUNT(*) FROM words 
                    WHERE UPPER(SUBSTR(informal_text, 1, 1)) = ? OR LOWER(SUBSTR(informal_text, 1, 1)) = ?
                ''', (letter, letter.lower()))
            
            result = self.__cur.fetchone()
            return result[0] if result else 0
        except sqlite3.Error as e:
            print(f"❌ Ошибка подсчета слов по букве {letter}: {e}")
            return 0

    def get_alphabet_stats(self) -> Dict[str, int]:
        """Получить статистику по буквам алфавита"""
        try:
            # Получаем статистику по русским буквам (и верхний и нижний регистр)
            russian_letters = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
            stats = {}
            
            for letter in russian_letters:
                self.__cur.execute('''
                    SELECT COUNT(*) FROM words 
                    WHERE UPPER(SUBSTR(informal_text, 1, 1)) = ? OR LOWER(SUBSTR(informal_text, 1, 1)) = ?
                ''', (letter, letter.lower()))
                result = self.__cur.fetchone()
                if result and result[0] > 0:
                    stats[letter] = result[0]
            
            # Добавляем счетчик для цифр
            self.__cur.execute('''
                SELECT COUNT(*) FROM words 
                WHERE (
                    informal_text LIKE '0%' OR informal_text LIKE '1%' OR 
                    informal_text LIKE '2%' OR informal_text LIKE '3%' OR 
                    informal_text LIKE '4%' OR informal_text LIKE '5%' OR 
                    informal_text LIKE '6%' OR informal_text LIKE '7%' OR 
                    informal_text LIKE '8%' OR informal_text LIKE '9%'
                )
            ''')
            result = self.__cur.fetchone()
            if result and result[0] > 0:
                stats['0-9'] = result[0]
            
            return stats
        except sqlite3.Error as e:
            print(f"❌ Ошибка получения статистики алфавита: {e}")
            return {}
#pragma endregion

#pragma region Profanity Methods
    def add_profanity_word(self, word: str) -> bool:
        try:
            self.__cur.execute(
                'INSERT OR IGNORE INTO profanity_words (word) VALUES (?)',
                (word.lower(),)
            )
            self.__db.commit()
            return True
        except sqlite3.Error as e:
            print(f"❌ Ошибка добавления матного слова: {e}")
            return False

    def get_profanity_words(self) -> List[str]:
        try:
            self.__cur.execute('SELECT word FROM profanity_words')
            return [row[0] for row in self.__cur.fetchall()]
        except sqlite3.Error as e:
            print(f"❌ Ошибка получения матных слов: {e}")
            return []

    def is_profanity(self, text: str) -> bool:
        try:
            words = self.get_profanity_words()
            text_lower = text.lower()
            
            # Проверяем каждое слово из текста
            for word in text_lower.split():
                if word in words:
                    return True
            
            # Проверяем словосочетания (до 3 слов)
            text_words = text_lower.split()
            for i in range(len(text_words)):
                for length in range(1, min(4, len(text_words) - i + 1)):
                    phrase = ' '.join(text_words[i:i + length])
                    if phrase in words:
                        return True
                        
            return False
        except sqlite3.Error as e:
            print(f"❌ Ошибка проверки на маты: {e}")
            return False

    def load_profanity_from_json(self, json_file_path: str) -> bool:
        """Загружает матные слова из JSON файла в базу данных"""
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                words_data = json.load(f)
            
            profanity_words = set()
            for item in words_data:
                # Добавляем неформальный текст как матное слово
                profanity_words.add(item['informal_text'].lower())
            
            # Очищаем таблицу перед загрузкой
            self.__cur.execute('DELETE FROM profanity_words')
            
            # Добавляем слова в базу
            for word in profanity_words:
                self.__cur.execute(
                    'INSERT INTO profanity_words (word) VALUES (?)',
                    (word,)
                )
            
            self.__db.commit()
            print(f"✅ Загружено {len(profanity_words)} матных слов из JSON")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка загрузки матных слов из JSON: {e}")
            return False
#pragma endregion

#pragma region Admin Methods
    def addAdmin(self, login, role: str):
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

    def getAdmin(self):
        try:
            self.__cur.execute("SELECT * FROM admins")
            res = self.__cur.fetchall()
            if res:
                return res
        except sqlite3.Error as e:
            print("Failed to get admins:", str(e))
        return []

    def removeAdminByID(self, AdminID):
        try:
            self.__cur.execute("DELETE FROM admins WHERE id=?", (AdminID,))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Failed to remove admin by id:", str(e))
#pragma endregion

#pragma region Statistics
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