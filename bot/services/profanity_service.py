import sqlite3
from database import FDataBase

def connect_db():
    return sqlite3.connect('translations.db')

class ProfanityService:
    def __init__(self, db: FDataBase):
        self.db = db

    def contains_profanity(self, text: str) -> bool:
        """Проверяет содержит ли текст матные слова"""
        return self.db.is_profanity(text)

    def get_profanity_message(self) -> str:
        """Возвращает сообщение о недопустимости матов"""
        return (
            "🚫 Использование нецензурной лексики не поддерживается.\n\n"
            "📝 Пожалуйста, выразите свою мысль в культурной форме.\n"
            "💡 Используйте вежливые выражения и литературные слова."
        )