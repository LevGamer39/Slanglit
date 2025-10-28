import sqlite3
from database import FDataBase

def connect_db():
    return sqlite3.connect('translations.db')

class HistoryService:
    def __init__(self, db: FDataBase):
        self.db = db

    def get_user_history(self, user_id: int, limit: int = 1000):
        return self.db.get_user_translations(user_id, limit)

    def search_user_history(self, search_text: str, user_id: int):
        return self.db.search_user_translations(search_text, user_id)